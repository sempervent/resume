from __future__ import annotations

from career_docs.cli import main
from career_docs.errors import CareerDocsError


def test_validate_command(repo_root):
    assert main(["--root", str(repo_root), "validate"]) == 0


def test_profiles_command(repo_root, capsys):
    assert main(["--root", str(repo_root), "profiles"]) == 0
    output = capsys.readouterr().out
    for profile_id in (
        "data_architect",
        "staff_engineer",
        "geospatial_architect",
        "platform_engineer",
        "scientific_software",
        "academic_cv",
    ):
        assert profile_id in output


def test_build_requires_a_selection(repo_root):
    assert main(["--root", str(repo_root), "build"]) == 1


def test_missing_contact_flag_fails(repo_root, tmp_path):
    code = main(
        [
            "--root",
            str(repo_root),
            "build",
            "--profile",
            "staff_engineer",
            "--output",
            str(tmp_path / "out"),
            "--contact",
            "--contact-file",
            str(tmp_path / "missing.yaml"),
            "--skip-pdf",
        ]
    )
    assert code == 1


def test_cli_build_skip_pdf_accepts_spaced_output(repo_root, tmp_path):
    output = tmp_path / "build out"
    code = main(
        [
            "--root",
            str(repo_root),
            "build",
            "--profile",
            "platform_engineer",
            "--output",
            str(output),
            "--skip-pdf",
        ]
    )
    assert code == 0
    assert (output / "platform_engineer" / "resume.txt").is_file()


def test_audit_command(repo_root):
    assert main(["--root", str(repo_root), "audit"]) == 0


def test_unknown_profile_exits_nonzero(repo_root, tmp_path):
    code = main(
        [
            "--root",
            str(repo_root),
            "build",
            "--profile",
            "missing",
            "--output",
            str(tmp_path),
            "--skip-pdf",
        ]
    )
    assert code == 1
    assert CareerDocsError
