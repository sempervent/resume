"""Load YAML inventory files."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

import yaml

from career_docs.errors import CareerDocsError
from career_docs.models import (
    Achievement,
    Education,
    Employment,
    Identity,
    Profile,
    Project,
    SkillGroup,
    Summary,
)

DATA_FILES = {
    "identity": "identity.yaml",
    "experience": "experience.yaml",
    "achievements": "achievements.yaml",
    "skills": "skills.yaml",
    "projects": "projects.yaml",
    "education": "education.yaml",
    "summaries": "summaries.yaml",
}


@dataclass
class Inventory:
    root: Path
    identity: Identity
    employment: list[Employment]
    achievements: list[Achievement]
    skills: list[SkillGroup]
    projects: list[Project]
    education: list[Education]
    summaries: list[Summary]
    profiles: list[Profile]

    def employment_map(self) -> dict[str, Employment]:
        return {item.id: item for item in self.employment}

    def achievement_map(self) -> dict[str, Achievement]:
        return {item.id: item for item in self.achievements}

    def project_map(self) -> dict[str, Project]:
        return {item.id: item for item in self.projects}

    def skill_map(self) -> dict[str, SkillGroup]:
        return {item.id: item for item in self.skills}

    def summary_map(self) -> dict[str, Summary]:
        return {item.id: item for item in self.summaries}

    def profile_map(self) -> dict[str, Profile]:
        return {item.id: item for item in self.profiles}


def find_root(start: Path | None = None) -> Path:
    env = os.environ.get("CAREER_DOCS_ROOT")
    if env:
        return Path(env).resolve()
    if start is not None:
        current = start.resolve()
    else:
        current = Path(__file__).resolve()
    for candidate in [current, *current.parents]:
        if (candidate / "pyproject.toml").is_file() and (candidate / "data").is_dir():
            return candidate
    raise CareerDocsError("Could not locate the career-docs repository root.")


def _read_yaml(path: Path) -> object:
    if not path.is_file():
        raise CareerDocsError(f"Missing required file: {path}")
    try:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise CareerDocsError(f"Invalid YAML in {path}: {exc}") from exc
    if loaded is None:
        raise CareerDocsError(f"{path} is empty")
    return loaded


def _mapping(path: Path) -> dict:
    loaded = _read_yaml(path)
    if not isinstance(loaded, dict):
        raise CareerDocsError(f"{path} must contain a YAML mapping")
    return loaded


def _require_list(data: dict, key: str, path: Path) -> list:
    value = data.get(key)
    if not isinstance(value, list):
        raise CareerDocsError(f"{path} must contain a '{key}' list")
    return value


def load_inventory(root: Path | None = None) -> Inventory:
    repo = find_root() if root is None else root.resolve()
    data_dir = repo / "data"
    profile_dir = repo / "profiles"
    try:
        identity = Identity.model_validate(_mapping(data_dir / "identity.yaml"))
        experience_doc = _mapping(data_dir / "experience.yaml")
        achievement_doc = _mapping(data_dir / "achievements.yaml")
        skill_doc = _mapping(data_dir / "skills.yaml")
        project_doc = _mapping(data_dir / "projects.yaml")
        education_doc = _mapping(data_dir / "education.yaml")
        summary_doc = _mapping(data_dir / "summaries.yaml")
        employment = [
            Employment.model_validate(item)
            for item in _require_list(experience_doc, "records", data_dir / "experience.yaml")
        ]
        achievements = [
            Achievement.model_validate(item)
            for item in _require_list(
                achievement_doc, "achievements", data_dir / "achievements.yaml"
            )
        ]
        skills = [
            SkillGroup.model_validate(item)
            for item in _require_list(skill_doc, "groups", data_dir / "skills.yaml")
        ]
        projects = [
            Project.model_validate(item)
            for item in _require_list(project_doc, "projects", data_dir / "projects.yaml")
        ]
        education = [
            Education.model_validate(item)
            for item in _require_list(education_doc, "records", data_dir / "education.yaml")
        ]
        summaries = [
            Summary.model_validate(item)
            for item in _require_list(summary_doc, "summaries", data_dir / "summaries.yaml")
        ]
    except CareerDocsError:
        raise
    except Exception as exc:
        raise CareerDocsError(f"Canonical data failed validation: {exc}") from exc

    profiles: list[Profile] = []
    if not profile_dir.is_dir():
        raise CareerDocsError(f"Missing profiles directory: {profile_dir}")
    for path in sorted(profile_dir.glob("*.yaml")):
        try:
            profiles.append(Profile.model_validate(_mapping(path)))
        except Exception as exc:
            raise CareerDocsError(f"Profile {path.name} failed validation: {exc}") from exc
    if not profiles:
        raise CareerDocsError(f"No profiles found in {profile_dir}")

    return Inventory(
        root=repo,
        identity=identity,
        employment=employment,
        achievements=achievements,
        skills=skills,
        projects=projects,
        education=education,
        summaries=summaries,
        profiles=profiles,
    )
