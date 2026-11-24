"""Build a render view and write TeX, Markdown, and plain text."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from career_docs.errors import CareerDocsError
from career_docs.load import Inventory
from career_docs.models import (
    Achievement,
    Employment,
    Metric,
    PrivateContact,
    Profile,
    Project,
    VerificationStatus,
    format_range,
)
from career_docs.publications import Publication, load_publications
from career_docs.textutil import is_public, latex_escape, latex_url

SECTION_TITLES = {
    "summary": "Professional Summary",
    "skills": "Technical Skills",
    "experience": "Professional Experience",
    "projects": "Selected Projects",
    "education": "Education",
    "publications": "Publications",
}


@dataclass
class RoleView:
    title: str
    organization: str
    location: str
    dates: str
    dates_latex: str
    bullets: list[str]
    responsibilities: list[str] = field(default_factory=list)


@dataclass
class SkillView:
    label: str
    items: str


@dataclass
class ProjectView:
    name: str
    url: str | None
    summary: str
    technologies: str
    review_required: bool


@dataclass
class EducationView:
    credential: str
    organization: str
    detail: str


@dataclass
class PublicationView:
    year: int
    authors: str
    title: str
    title_text: str
    venue: str
    venue_text: str
    url: str


@dataclass
class ContactPart:
    kind: str
    text: str
    url: str | None = None


@dataclass
class DocumentView:
    name: str
    headline: str
    tagline: str
    document_name: str
    document_kind: str
    summary: str
    summary_requires_review: bool
    contact_parts: list[ContactPart]
    links: list[dict[str, str]]
    skills: list[SkillView]
    roles: list[RoleView]
    projects: list[ProjectView]
    education: list[EducationView]
    publications: list[PublicationView]
    sections: list[dict[str, str]]
    achievement_ids: list[str]
    project_ids: list[str]


def organization_line(record: Employment) -> str:
    if record.organization_detail:
        return f"{record.organization_detail}, {record.organization}"
    return record.organization


def location_line(record: Employment) -> str:
    parts: list[str] = []
    if record.location:
        parts.append(record.location)
    if record.remote_status == "remote":
        parts.append("Remote")
    elif record.remote_status == "hybrid":
        parts.append("Hybrid")
    return " (".join(parts) + ")" if len(parts) == 2 else (parts[0] if parts else "")


def renderable_metrics(achievement: Achievement) -> list[Metric]:
    allowed = {VerificationStatus.source_supported, VerificationStatus.independently_checked}
    return [
        metric
        for metric in achievement.metrics
        if metric.verification.status in allowed and not metric.review_required
    ]


def _skill_items(group_items: list) -> str:
    rendered: list[str] = []
    for item in group_items:
        if item.detail:
            rendered.append(f"{item.name} ({item.detail})")
        else:
            rendered.append(item.name)
    return ", ".join(rendered)


def build_view(
    inventory: Inventory,
    profile: Profile,
    *,
    achievement_ids: list[str] | None = None,
    project_ids: list[str] | None = None,
    summary_override: str | None = None,
    contact: PrivateContact | None = None,
    publications: list[Publication] | None = None,
) -> DocumentView:
    employment = inventory.employment_map()
    achievements = inventory.achievement_map()
    projects = inventory.project_map()
    skills = inventory.skill_map()
    summary = inventory.summary_map()[profile.summary_id]

    selected_ids = achievement_ids if achievement_ids is not None else None
    roles: list[RoleView] = []
    used_achievements: list[str] = []

    role_order = [role.employment_id for role in profile.roles]
    extra_ids: list[str] = []
    if selected_ids is not None:
        for achievement_id in selected_ids:
            achievement = _public_achievement(achievements, achievement_id)
            if (
                achievement.employment_id not in role_order
                and achievement.employment_id not in extra_ids
            ):
                extra_ids.append(achievement.employment_id)
    ordered_employment = role_order + extra_ids

    for employment_id in ordered_employment:
        record = employment.get(employment_id)
        if record is None or not is_public(record.visibility):
            raise CareerDocsError(
                f"Employment {employment_id} is not available for a public document"
            )
        if selected_ids is None:
            profile_role = next(
                role for role in profile.roles if role.employment_id == employment_id
            )
            chosen = list(profile_role.achievement_ids)
        else:
            chosen = [
                achievement_id
                for achievement_id in selected_ids
                if achievements[achievement_id].employment_id == employment_id
            ]
        if not chosen:
            continue
        bullets: list[str] = []
        for achievement_id in chosen:
            achievement = _public_achievement(achievements, achievement_id)
            bullets.append(achievement.statement.strip())
            metrics = renderable_metrics(achievement)
            for metric in metrics:
                unit = f" {metric.unit}" if metric.unit else ""
                bullets.append(f"{metric.name}: {metric.value}{unit}")
            used_achievements.append(achievement_id)
        roles.append(
            RoleView(
                title=record.title,
                organization=organization_line(record),
                location=location_line(record),
                dates=format_range(record.start, record.end, dash="–"),
                dates_latex=format_range(record.start, record.end, dash="--"),
                bullets=bullets,
                responsibilities=list(record.responsibilities),
            )
        )

    if not roles:
        raise CareerDocsError(f"Profile {profile.id} resolved to an empty employment history")

    chosen_projects = project_ids if project_ids is not None else list(profile.project_ids)
    project_views: list[ProjectView] = []
    for project_id in chosen_projects:
        project = projects.get(project_id)
        if project is None:
            raise CareerDocsError(f"Unknown project id: {project_id}")
        if not is_public(project.visibility):
            raise CareerDocsError(f"Project {project_id} is not public and cannot be rendered")
        project_views.append(
            ProjectView(
                name=project.name,
                url=project.url,
                summary=project.summary.strip(),
                technologies=", ".join(project.technologies),
                review_required=project.review_required,
            )
        )

    skill_views: list[SkillView] = []
    for skill_id in profile.skill_group_ids:
        group = skills[skill_id]
        if not is_public(group.visibility):
            raise CareerDocsError(f"Skill group {skill_id} is not public")
        skill_views.append(SkillView(label=group.label, items=_skill_items(group.items)))

    education_views: list[EducationView] = []
    for record in inventory.education:
        if not is_public(record.visibility):
            continue
        credential = record.credential
        if record.field:
            credential = f"{credential}, {record.field}"
        detail_parts = [record.date_display]
        if profile.show_gpa and record.gpa:
            detail_parts.append(f"GPA {record.gpa}")
        if record.honors:
            detail_parts.append(record.honors)
        education_views.append(
            EducationView(
                credential=credential,
                organization=record.organization,
                detail=", ".join(detail_parts),
            )
        )

    publication_views: list[PublicationView] = []
    if "publications" in profile.sections:
        loaded = publications
        if loaded is None:
            loaded = load_publications(inventory.root / "data" / "publications.bib")
        publication_views = [
            PublicationView(
                year=item.year,
                authors=item.authors,
                title=item.title,
                title_text=item.title_text,
                venue=item.venue,
                venue_text=item.venue_text,
                url=item.url,
            )
            for item in loaded
        ]

    contact_parts = [ContactPart("text", inventory.identity.location_display)]
    if contact is not None:
        if contact.phone:
            contact_parts.append(ContactPart("phone", contact.phone))
        if contact.email:
            contact_parts.append(ContactPart("email", contact.email, url=f"mailto:{contact.email}"))

    summary_text = summary_override.strip() if summary_override else summary.text.strip()
    return DocumentView(
        name=inventory.identity.name,
        headline=inventory.identity.headline,
        tagline=inventory.identity.tagline,
        document_name=profile.document_name,
        document_kind=profile.document_kind,
        summary=summary_text,
        summary_requires_review=summary_override is not None,
        contact_parts=contact_parts,
        links=[{"label": link.label, "url": link.url} for link in inventory.identity.links],
        skills=skill_views,
        roles=roles,
        projects=project_views,
        education=education_views,
        publications=publication_views,
        sections=[
            {"id": section, "title": SECTION_TITLES[section]} for section in profile.sections
        ],
        achievement_ids=used_achievements,
        project_ids=chosen_projects,
    )


def _public_achievement(achievements: dict[str, Achievement], achievement_id: str) -> Achievement:
    achievement = achievements.get(achievement_id)
    if achievement is None:
        raise CareerDocsError(f"Unknown achievement id: {achievement_id}")
    if not is_public(achievement.visibility):
        raise CareerDocsError(
            f"Achievement {achievement_id} is {achievement.visibility.value} and cannot be rendered"
        )
    return achievement


def template_env(root: Path) -> Environment:
    environment = Environment(
        loader=FileSystemLoader(root / "templates"),
        autoescape=False,
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )
    environment.filters["latex"] = latex_escape
    environment.filters["latex_url"] = latex_url
    return environment


def render_templates(root: Path, view: DocumentView) -> dict[str, str]:
    environment = template_env(root)
    stem = "academic_cv" if view.document_kind == "academic_cv" else "resume"
    return {
        "tex": environment.get_template(f"{stem}.tex.j2").render(doc=view),
        "md": environment.get_template("resume.md.j2").render(doc=view),
        "txt": environment.get_template("resume.txt.j2").render(doc=view),
    }


def assert_no_template_residue(outputs: dict[str, str]) -> None:
    for name, content in outputs.items():
        if "{{" in content or "{%" in content:
            raise CareerDocsError(f"Unresolved template expression in {name} output")


def write_document_set(directory: Path, stem: str, outputs: dict[str, str]) -> dict[str, Path]:
    directory.mkdir(parents=True, exist_ok=True)
    written: dict[str, Path] = {}
    for kind, content in outputs.items():
        path = directory / f"{stem}.{kind}"
        path.write_text(content, encoding="utf-8")
        written[kind] = path
    return written


def public_project(inventory: Inventory, project_id: str) -> Project:
    project = inventory.project_map().get(project_id)
    if project is None:
        raise CareerDocsError(f"Unknown project id: {project_id}")
    if not is_public(project.visibility):
        raise CareerDocsError(f"Project {project_id} is not public and cannot be rendered")
    return project
