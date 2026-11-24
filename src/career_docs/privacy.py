"""Private contact loading and output-path checks."""

from __future__ import annotations

import subprocess
from pathlib import Path

import yaml

from career_docs.errors import CareerDocsError
from career_docs.models import PrivateContact

FORBIDDEN_CONTACT_KEYS = {"address", "street", "street_address", "postal_code", "zip"}


def load_private_contact(path: Path) -> PrivateContact:
    if not path.is_file():
        raise CareerDocsError(
            f"Missing private contact file: {path}. Copy config/private.example.yaml "
            "to config/private.yaml and add the details you want on a local résumé."
        )
    try:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise CareerDocsError(f"Invalid YAML in {path}: {exc}") from exc
    if not isinstance(loaded, dict):
        raise CareerDocsError(f"{path} must contain a YAML mapping")
    present = FORBIDDEN_CONTACT_KEYS & set(loaded)
    if present:
        names = ", ".join(sorted(present))
        raise CareerDocsError(
            f"{path} contains {names}. Résumés print city and region from identity.yaml, "
            "not a street address."
        )
    try:
        contact = PrivateContact.model_validate(loaded)
    except Exception as exc:
        raise CareerDocsError(f"Invalid private contact file: {exc}") from exc
    if not contact.email and not contact.phone:
        raise CareerDocsError(f"{path} must include an email, a phone number, or both.")
    return contact


def ensure_application_output_is_private(root: Path, output_dir: Path) -> None:
    """Refuse application artifacts that would land in a committable repository path."""
    resolved = output_dir.resolve()
    repo = root.resolve()
    if resolved != repo and repo not in resolved.parents:
        return
    completed = subprocess.run(
        ["git", "check-ignore", "-q", "--", str(resolved)],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise CareerDocsError(
            f"Refusing to write application documents to {resolved}. "
            "That path is inside the repository and is not gitignored. "
            "Use a directory outside the checkout or a gitignored directory such as private/."
        )
