"""Write JSON Schema files from the Pydantic models."""

from __future__ import annotations

import json
from pathlib import Path

from career_docs.application import ApplicationSpec
from career_docs.models import (
    Achievement,
    Education,
    Employment,
    Identity,
    PrivateContact,
    Profile,
    Project,
    SkillGroup,
    Summary,
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "schemas"

MODELS = {
    "identity.schema.json": Identity,
    "employment.schema.json": Employment,
    "achievement.schema.json": Achievement,
    "skill-group.schema.json": SkillGroup,
    "project.schema.json": Project,
    "education.schema.json": Education,
    "summary.schema.json": Summary,
    "profile.schema.json": Profile,
    "application.schema.json": ApplicationSpec,
    "private-contact.schema.json": PrivateContact,
}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, model in MODELS.items():
        schema = model.model_json_schema()
        (OUT / name).write_text(json.dumps(schema, indent=2) + "\n", encoding="utf-8")
        print(f"wrote schemas/{name}")


if __name__ == "__main__":
    main()
