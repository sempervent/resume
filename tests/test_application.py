from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from career_docs.application import generate_application, load_application
from career_docs.errors import CareerDocsError
from career_docs.privacy import ensure_application_output_is_private, load_private_contact
from career_docs.textutil import word_count


def test_example_application_builds(inventory, tmp_path: Path):
    spec = load_application(inventory.root / "examples" / "application.example.yaml")
    output = tmp_path / "Example Company"
    manifest = generate_application(inventory, spec, output, compile_pdf=False)
    assert (output / "resume.md").is_file()
    assert (output / "resume.txt").is_file()
    assert (output / "cover_letter.txt").is_file()
    assert (output / "manifest.yaml").is_file()
    text = (output / "resume.txt").read_text(encoding="utf-8")
    assert "Example Company" not in text
    assert "Prefect 1 to Prefect 2" in text
    assert "GeoParquet" in text
    letter = (output / "cover_letter.txt").read_text(encoding="utf-8")
    assert "Example Company" in letter
    assert "Staff Data Engineer" in letter
    assert 200 <= manifest["cover_letter_word_count"] <= 300
    assert 200 <= word_count(letter) <= 360
    loaded = yaml.safe_load((output / "manifest.yaml").read_text(encoding="utf-8"))
    assert loaded["distribution"] == "private"
    assert loaded["profile"] == "data_architect"
    ids = [item["id"] for item in loaded["resume_achievements"]]
    assert set(ids) == set(spec.selected_achievements)
    assert manifest["cover_letter_word_count"] == loaded["cover_letter_word_count"]


def test_unknown_achievement_is_rejected(inventory, tmp_path: Path):
    spec = load_application(inventory.root / "examples" / "application.example.yaml")
    spec.selected_achievements = ["this-id-does-not-exist"]
    with pytest.raises(CareerDocsError, match="this-id-does-not-exist"):
        generate_application(inventory, spec, tmp_path / "out", compile_pdf=False)


def test_unknown_profile_is_rejected(inventory):
    spec = load_application(inventory.root / "examples" / "application.example.yaml")
    spec.profile = "not-a-profile"
    with pytest.raises(CareerDocsError, match="not-a-profile"):
        generate_application(inventory, spec, Path("/tmp"), compile_pdf=False)


def test_invalid_application_yaml(tmp_path: Path):
    path = tmp_path / "bad.yaml"
    path.write_text("company: Only Company\n", encoding="utf-8")
    with pytest.raises(CareerDocsError, match="Invalid application"):
        load_application(path)


def test_missing_contact_file(tmp_path: Path):
    with pytest.raises(CareerDocsError, match="Missing private contact"):
        load_private_contact(tmp_path / "private.yaml")


def test_contact_file_rejects_street_address(tmp_path: Path):
    path = tmp_path / "private.yaml"
    path.write_text("email: ada@example.com\nstreet: 1 Main Street\n", encoding="utf-8")
    with pytest.raises(CareerDocsError, match="street"):
        load_private_contact(path)


def test_application_output_inside_repo_is_refused(inventory, tmp_path: Path):
    target = inventory.root / "not ignored application"
    with pytest.raises(CareerDocsError, match="gitignored"):
        ensure_application_output_is_private(inventory.root, target)


def test_paths_with_spaces(inventory, tmp_path: Path):
    spec = load_application(inventory.root / "examples" / "application.example.yaml")
    output = tmp_path / "My Application (draft)"
    generate_application(inventory, spec, output, compile_pdf=False)
    assert (output / "cover_letter.md").is_file()
