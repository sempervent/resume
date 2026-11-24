"""Cross-reference checks for canonical data and profiles."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from career_docs.load import Inventory
from career_docs.models import ALLOWED_CATEGORIES, SECTION_NAMES, Visibility
from career_docs.textutil import PLACEHOLDER_RE, is_public


@dataclass
class Issue:
    severity: Literal["error", "warning"]
    message: str


def _duplicates(ids: list[str]) -> list[str]:
    seen: set[str] = set()
    dupes: list[str] = []
    for item in ids:
        if item in seen and item not in dupes:
            dupes.append(item)
        seen.add(item)
    return dupes


def validate_inventory(inventory: Inventory) -> list[Issue]:
    issues: list[Issue] = []
    employment = inventory.employment_map()
    achievements = inventory.achievement_map()
    projects = inventory.project_map()
    skills = inventory.skill_map()
    summaries = inventory.summary_map()

    for label, ids in (
        ("employment", [item.id for item in inventory.employment]),
        ("achievement", [item.id for item in inventory.achievements]),
        ("project", [item.id for item in inventory.projects]),
        ("skill group", [item.id for item in inventory.skills]),
        ("education", [item.id for item in inventory.education]),
        ("summary", [item.id for item in inventory.summaries]),
        ("profile", [item.id for item in inventory.profiles]),
    ):
        for duplicate in _duplicates(ids):
            issues.append(Issue("error", f"Duplicate {label} id: {duplicate}"))

    for record in inventory.employment:
        if record.featured and not record.achievement_ids:
            issues.append(Issue("error", f"Featured employment {record.id} has no achievement ids"))
        for achievement_id in record.achievement_ids:
            achievement = achievements.get(achievement_id)
            if achievement is None:
                issues.append(
                    Issue(
                        "error",
                        f"Employment {record.id} references unknown achievement {achievement_id}",
                    )
                )
            elif achievement.employment_id != record.id:
                issues.append(
                    Issue(
                        "error",
                        f"Achievement {achievement_id} is listed on {record.id} "
                        f"but points at {achievement.employment_id}",
                    )
                )

    listed: set[str] = set()
    for record in inventory.employment:
        listed.update(record.achievement_ids)
    for achievement in inventory.achievements:
        if achievement.employment_id not in employment:
            issues.append(
                Issue(
                    "error",
                    f"Achievement {achievement.id} references unknown employment "
                    f"{achievement.employment_id}",
                )
            )
        if achievement.id not in listed:
            issues.append(
                Issue(
                    "error",
                    f"Achievement {achievement.id} is not listed on its employment record",
                )
            )
        for category in achievement.categories:
            if category not in ALLOWED_CATEGORIES:
                issues.append(
                    Issue("error", f"Achievement {achievement.id} has unknown category {category}")
                )
        if PLACEHOLDER_RE.search(achievement.statement):
            issues.append(
                Issue("error", f"Achievement {achievement.id} contains a placeholder token")
            )
        for metric in achievement.metrics:
            if metric.verification.status.value == "owner-verification-required":
                issues.append(
                    Issue(
                        "warning",
                        f"Metric {metric.name} on {achievement.id} is not verified "
                        "and will not be rendered",
                    )
                )
            if PLACEHOLDER_RE.search(metric.value):
                issues.append(
                    Issue("error", f"Metric {metric.name} on {achievement.id} is a placeholder")
                )

    for summary in inventory.summaries:
        if PLACEHOLDER_RE.search(summary.text):
            issues.append(Issue("error", f"Summary {summary.id} contains a placeholder token"))

    for profile in inventory.profiles:
        if profile.summary_id not in summaries:
            issues.append(
                Issue(
                    "error", f"Profile {profile.id} references unknown summary {profile.summary_id}"
                )
            )
        if profile.document_kind == "resume" and profile.page_limit != 2:
            issues.append(Issue("error", f"Commercial profile {profile.id} must set page_limit: 2"))
        if profile.document_kind == "academic_cv" and profile.page_limit is not None:
            issues.append(Issue("error", "The academic CV must not set a commercial page limit"))
        unknown_sections = [name for name in profile.sections if name not in SECTION_NAMES]
        for name in unknown_sections:
            issues.append(Issue("error", f"Profile {profile.id} has unknown section {name}"))
        if list(profile.sections) != list(dict.fromkeys(profile.sections)):
            issues.append(Issue("error", f"Profile {profile.id} repeats a section"))
        for skill_id in profile.skill_group_ids:
            group = skills.get(skill_id)
            if group is None:
                issues.append(
                    Issue(
                        "error", f"Profile {profile.id} references unknown skill group {skill_id}"
                    )
                )
            elif not is_public(group.visibility):
                issues.append(
                    Issue(
                        "error",
                        f"Profile {profile.id} references non-public skill group {skill_id}",
                    )
                )
        seen_roles: set[str] = set()
        for role in profile.roles:
            if role.employment_id in seen_roles:
                issues.append(
                    Issue(
                        "error",
                        f"Profile {profile.id} repeats employment {role.employment_id}",
                    )
                )
            seen_roles.add(role.employment_id)
            record = employment.get(role.employment_id)
            if record is None:
                issues.append(
                    Issue(
                        "error",
                        f"Profile {profile.id} references unknown employment {role.employment_id}",
                    )
                )
                continue
            if not is_public(record.visibility):
                issues.append(
                    Issue(
                        "error",
                        f"Profile {profile.id} references non-public employment {record.id}",
                    )
                )
            for achievement_id in role.achievement_ids:
                achievement = achievements.get(achievement_id)
                if achievement is None:
                    issues.append(
                        Issue(
                            "error",
                            f"Profile {profile.id} references unknown achievement {achievement_id}",
                        )
                    )
                    continue
                if achievement.employment_id != record.id:
                    issues.append(
                        Issue(
                            "error",
                            f"Profile {profile.id} places {achievement_id} under {record.id}, "
                            f"but it belongs to {achievement.employment_id}",
                        )
                    )
                if achievement.visibility != Visibility.public:
                    issues.append(
                        Issue(
                            "error",
                            f"Profile {profile.id} references non-public achievement "
                            f"{achievement_id}",
                        )
                    )
        for project_id in profile.project_ids:
            project = projects.get(project_id)
            if project is None:
                issues.append(
                    Issue("error", f"Profile {profile.id} references unknown project {project_id}")
                )
            elif project.visibility != Visibility.public:
                issues.append(
                    Issue(
                        "error",
                        f"Profile {profile.id} references non-public project {project_id}",
                    )
                )

    return issues


def error_issues(issues: list[Issue]) -> list[Issue]:
    return [issue for issue in issues if issue.severity == "error"]
