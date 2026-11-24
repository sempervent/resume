from __future__ import annotations

import subprocess

from career_docs.cli import main


def personal_markers() -> list[str]:
    return [
        "12918 " + "Sanderling Lane",
        "547 " + "Murray Drive",
        "jngrant" + "@" + "live.com",
        "jngrant9" + "@" + "gmail.com",
        "(865) " + "803-3495",
        "(865) " + "803 3495",
    ]


NEW_PREFIXES = (
    "data",
    "profiles",
    "templates",
    "docs",
    "prompts",
    "examples",
    "src",
    "config",
    "schemas",
    "archive",
)


def test_new_tree_omits_personal_contact(repo_root):
    markers = personal_markers()
    offenders: list[str] = []
    for prefix in NEW_PREFIXES:
        directory = repo_root / prefix
        if not directory.exists():
            continue
        for path in directory.rglob("*"):
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            for marker in markers:
                if marker in text:
                    offenders.append(f"{path.relative_to(repo_root)}: {marker}")
    assert offenders == []


def test_tracked_tex_omits_street_addresses(repo_root):
    completed = subprocess.run(
        ["git", "ls-files", "-z", "*.tex"],
        cwd=repo_root,
        capture_output=True,
        check=True,
    )
    markers = ["12918 " + "Sanderling Lane", "547 " + "Murray Drive"]
    offenders: list[str] = []
    for name in completed.stdout.decode().split("\0"):
        if not name:
            continue
        text = (repo_root / name).read_text(encoding="utf-8", errors="replace")
        for marker in markers:
            if marker in text:
                offenders.append(name)
    assert offenders == []


def test_export_context_has_no_contact_details(inventory, tmp_path, repo_root):
    destination = tmp_path / "context.md"
    assert (
        main(
            [
                "--root",
                str(repo_root),
                "export-context",
                "--profile",
                "staff_engineer",
                "--output",
                str(destination),
            ]
        )
        == 0
    )
    text = destination.read_text(encoding="utf-8")
    assert "bold-penguin-prefect-migration" in text
    assert "Do not invent metrics" in text
    for marker in personal_markers():
        assert marker not in text
    assert "ada@example.com" not in text
