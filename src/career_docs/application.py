"""Validate an application file and render a private résumé plus cover letter."""

from __future__ import annotations

from datetime import date, datetime
from pathlib import Path

import yaml
from jinja2 import StrictUndefined
from pydantic import BaseModel, Field, ValidationError, field_validator

from career_docs.errors import CareerDocsError
from career_docs.load import Inventory
from career_docs.models import PrivateContact, Profile
from career_docs.pdf import compile_latex
from career_docs.render import (
    DocumentView,
    assert_no_template_residue,
    build_view,
    render_templates,
    template_env,
    write_document_set,
)
from career_docs.textutil import word_count


class RemoteSpec(BaseModel):
    classification: str = "unknown"
    tennessee_eligible: str = "unknown"


class CompensationSpec(BaseModel):
    currency: str = "USD"
    base_minimum: int | None = None
    base_maximum: int | None = None


class CoverLetterSpec(BaseModel):
    salutation: str = "Dear Hiring Team"
    paragraphs: list[str] = Field(default_factory=list)
    closing: str = "Sincerely,"
    date: str | None = None

    @field_validator("date", mode="before")
    @classmethod
    def date_to_iso(cls, value: object) -> object:
        if isinstance(value, datetime):
            return value.date().isoformat()
        if isinstance(value, date):
            return value.isoformat()
        return value


class ApplicationSpec(BaseModel):
    company: str
    position: str
    job_url: str | None = None
    profile: str
    remote: RemoteSpec = Field(default_factory=RemoteSpec)
    compensation: CompensationSpec = Field(default_factory=CompensationSpec)
    requirements: list[str] = Field(default_factory=list)
    selected_achievements: list[str] = Field(default_factory=list)
    selected_projects: list[str] = Field(default_factory=list)
    summary: str | None = None
    cover_letter: CoverLetterSpec = Field(default_factory=CoverLetterSpec)


def load_application(path: Path) -> ApplicationSpec:
    if not path.is_file():
        raise CareerDocsError(f"Application file not found: {path}")
    try:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise CareerDocsError(f"Invalid YAML in {path}: {exc}") from exc
    if not isinstance(loaded, dict):
        raise CareerDocsError(f"{path} must contain a YAML mapping")
    try:
        return ApplicationSpec.model_validate(loaded)
    except ValidationError as exc:
        raise CareerDocsError(f"Invalid application file:\n{exc}") from exc


def _profile(inventory: Inventory, profile_id: str) -> Profile:
    profile = inventory.profile_map().get(profile_id)
    if profile is None:
        known = ", ".join(sorted(inventory.profile_map()))
        raise CareerDocsError(f"Unknown profile '{profile_id}'. Known profiles: {known}")
    return profile


def _join_requirements(requirements: list[str]) -> str:
    if len(requirements) == 1:
        return requirements[0]
    return ", ".join(requirements[:-1]) + f", and {requirements[-1]}"


def cover_letter_paragraphs(
    inventory: Inventory,
    spec: ApplicationSpec,
    achievement_ids: list[str],
) -> tuple[list[str], list[str], bool]:
    """Return paragraphs, evidence ids, and whether the prose was supplied by the caller."""
    if spec.cover_letter.paragraphs:
        if len(spec.cover_letter.paragraphs) < 2:
            raise CareerDocsError("A supplied cover letter needs at least two paragraphs.")
        return list(spec.cover_letter.paragraphs), list(achievement_ids[:3]), True

    evidence = list(achievement_ids[:3])
    profile = _profile(inventory, spec.profile)
    if len(evidence) < 2:
        for role in profile.roles:
            for achievement_id in role.achievement_ids:
                if achievement_id not in evidence:
                    evidence.append(achievement_id)
                if len(evidence) == 3:
                    break
            if len(evidence) == 3:
                break
    if len(evidence) < 2:
        raise CareerDocsError(
            "Need at least two public achievements to write a cover letter. "
            "Select them in the application file or choose a fuller profile."
        )

    achievements = inventory.achievement_map()
    if spec.requirements:
        shown = _join_requirements(spec.requirements[:4])
        requirement_sentence = f"The posting emphasizes {shown}."
    else:
        requirement_sentence = (
            "The posting asks for production experience with data systems and software delivery."
        )
    opening = (
        f"I am applying for the {spec.position} position at {spec.company}. "
        f"I am a data and software systems architect who designs platforms and still writes "
        f"the software. Recent work includes geospatial data systems at Oak Ridge National "
        f"Laboratory and remote commercial data engineering at Bold Penguin. "
        f"{requirement_sentence} Those are systems I have designed and operated, and I am looking "
        f"for a role where that mix of architecture and implementation is the job."
    )
    statements = [achievements[item].statement.strip() for item in evidence]
    evidence_paragraph = "The work most relevant to this role is specific. " + " ".join(statements)
    closing = (
        f"That record spans commercial delivery and national-laboratory research software. "
        f"At Bold Penguin the work was remote and centered on AWS-backed workflows, "
        f"document-processing services, and shared delivery automation. At Oak Ridge it is "
        f"geospatial storage, processing, orchestration, and the services around them. "
        f"I would bring that combination of architectural ownership and hands-on implementation "
        f"to {spec.company}. Thank you for considering my application."
    )
    return [opening, evidence_paragraph, closing], evidence, False


def render_cover_letter(
    inventory: Inventory,
    spec: ApplicationSpec,
    paragraphs: list[str],
    contact: PrivateContact | None,
) -> dict[str, str]:
    date_display = format_cover_date(spec.cover_letter.date) if spec.cover_letter.date else ""
    salutation = spec.cover_letter.salutation.rstrip()
    if salutation[-1:] not in {",", ":", "!"}:
        salutation = f"{salutation},"
    context = {
        "name": inventory.identity.name,
        "company": spec.company,
        "position": spec.position,
        "date": date_display,
        "salutation": salutation,
        "paragraphs": paragraphs,
        "closing": spec.cover_letter.closing,
        "location": inventory.identity.location_display,
        "email": contact.email if contact else None,
        "phone": contact.phone if contact else None,
        "links": [{"label": link.label, "url": link.url} for link in inventory.identity.links],
    }
    environment = template_env(inventory.root)
    environment.undefined = StrictUndefined
    tex = environment.get_template("cover_letter.tex.j2").render(**context)
    markdown = environment.get_template("cover_letter.md.j2").render(**context)
    plain = environment.get_template("cover_letter.txt.j2").render(**context)
    outputs = {"tex": tex, "md": markdown, "txt": plain}
    for name, content in outputs.items():
        if "{{" in content or "{%" in content:
            raise CareerDocsError(f"Unresolved template expression in cover letter {name}")
    return outputs


def format_cover_date(value: str) -> str:
    parts = value.split("-")
    if len(parts) != 3 or not all(part.isdigit() for part in parts):
        raise CareerDocsError("cover_letter.date must be an ISO date, YYYY-MM-DD.")
    year, month, day = (int(part) for part in parts)
    months = (
        "",
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    )
    if not 1 <= month <= 12 or not 1 <= day <= 31:
        raise CareerDocsError("cover_letter.date is not a valid calendar date.")
    return f"{months[month]} {day}, {year}"


def build_manifest(
    inventory: Inventory,
    spec: ApplicationSpec,
    view: DocumentView,
    letter_ids: list[str],
    letter_is_supplied: bool,
    artifacts: list[str],
) -> dict:
    achievement_map = inventory.achievement_map()
    project_map = inventory.project_map()
    return {
        "distribution": "private",
        "do_not_commit": True,
        "company": spec.company,
        "position": spec.position,
        "job_url": spec.job_url,
        "profile": spec.profile,
        "remote": spec.remote.model_dump(),
        "compensation": spec.compensation.model_dump(),
        "requirements": spec.requirements,
        "summary_source": "application-override" if view.summary_requires_review else "profile",
        "machine_validated": [
            "profile id",
            "achievement ids",
            "project ids",
            "visibility of selected records",
        ],
        "prose_requiring_human_review": _review_notes(view, letter_is_supplied),
        "note": (
            "Achievement and project ids were resolved against the canonical inventory. "
            "Supplied prose was not fact-checked."
        ),
        "resume_achievements": [
            {
                "id": achievement_id,
                "review_required": achievement_map[achievement_id].review_required,
                "verification": achievement_map[achievement_id].verification.status.value,
            }
            for achievement_id in view.achievement_ids
        ],
        "cover_letter_achievements": [
            {
                "id": achievement_id,
                "review_required": achievement_map[achievement_id].review_required,
                "verification": achievement_map[achievement_id].verification.status.value,
            }
            for achievement_id in letter_ids
        ],
        "projects": [
            {
                "id": project_id,
                "review_required": project_map[project_id].review_required,
                "ownership": project_map[project_id].ownership,
            }
            for project_id in view.project_ids
        ],
        "artifacts": artifacts,
    }


def _review_notes(view: DocumentView, letter_is_supplied: bool) -> list[str]:
    notes: list[str] = []
    if view.summary_requires_review:
        notes.append("The professional summary was supplied in the application file.")
    if letter_is_supplied:
        notes.append("Cover letter paragraphs were supplied and were not fact-checked.")
    else:
        notes.append(
            "Cover letter prose is a deterministic template filled with canonical achievement "
            "statements. Read it before sending."
        )
    for project in view.projects:
        if project.review_required:
            notes.append(f"Project {project.name} is marked review_required.")
    if not notes:
        notes.append(
            "No application-supplied prose was used. Canonical statements still deserve a read."
        )
    return notes


def generate_application(
    inventory: Inventory,
    spec: ApplicationSpec,
    output_dir: Path,
    contact: PrivateContact | None = None,
    *,
    compile_pdf: bool = True,
) -> dict:
    profile = _profile(inventory, spec.profile)
    achievement_ids = spec.selected_achievements or None
    project_ids = spec.selected_projects or None
    view = build_view(
        inventory,
        profile,
        achievement_ids=achievement_ids,
        project_ids=project_ids,
        summary_override=spec.summary,
        contact=contact,
    )
    paragraphs, letter_ids, supplied = cover_letter_paragraphs(
        inventory, spec, view.achievement_ids
    )
    resume_outputs = render_templates(inventory.root, view)
    assert_no_template_residue(resume_outputs)
    letter_outputs = render_cover_letter(inventory, spec, paragraphs, contact)
    written = write_document_set(output_dir, profile.output_stem, resume_outputs)
    letter_paths = write_document_set(output_dir, "cover_letter", letter_outputs)
    artifacts = [path.name for path in [*written.values(), *letter_paths.values()]]
    if compile_pdf:
        resume_pdf = compile_latex(written["tex"])
        letter_pdf = compile_latex(letter_paths["tex"])
        artifacts.extend([resume_pdf.name, letter_pdf.name])
    manifest = build_manifest(inventory, spec, view, letter_ids, supplied, sorted(set(artifacts)))
    manifest["cover_letter_word_count"] = word_count(" ".join(paragraphs))
    manifest_path = output_dir / "manifest.yaml"
    manifest_path.write_text(
        yaml.safe_dump(manifest, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    manifest["manifest"] = manifest_path.name
    return manifest
