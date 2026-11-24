from __future__ import annotations

from pathlib import Path

import pytest

from career_docs.application import generate_application, load_application
from career_docs.pdf import compile_latex, pdf_page_count, pdf_text, pdflatex_available
from career_docs.render import build_view, render_templates, write_document_set

pytestmark = pytest.mark.skipif(not pdflatex_available(), reason="pdflatex is not installed")

COMMERCIAL = [
    "data_architect",
    "staff_engineer",
    "geospatial_architect",
    "platform_engineer",
    "scientific_software",
]


def _render_pdf(inventory, profile_id: str, directory: Path) -> tuple[Path, str]:
    profile = inventory.profile_map()[profile_id]
    view = build_view(inventory, profile)
    outputs = render_templates(inventory.root, view)
    written = write_document_set(directory, profile.output_stem, outputs)
    pdf = compile_latex(written["tex"])
    return pdf, pdf_text(pdf)


@pytest.mark.parametrize("profile_id", COMMERCIAL + ["academic_cv"])
def test_profile_pdf_compiles_and_extracts(inventory, tmp_path: Path, profile_id: str):
    pdf, text = _render_pdf(inventory, profile_id, tmp_path / profile_id)
    assert pdf.stat().st_size > 1000
    assert len(text.strip()) > 400
    assert "Joshua N. Grant" in text
    assert "Oak Ridge National Laboratory" in text
    assert "Bold Penguin" in text
    assert "{{" not in text
    assert "TODO" not in text
    assert "XX%" not in text
    for marker in ("12918", "Sanderling", "Murray Drive", "jngrant@live.com", "803-3495"):
        assert marker not in text


@pytest.mark.parametrize("profile_id", COMMERCIAL)
def test_commercial_resumes_are_at_most_two_pages(inventory, tmp_path: Path, profile_id: str):
    pdf, text = _render_pdf(inventory, profile_id, tmp_path / profile_id)
    assert pdf_page_count(pdf) <= 2
    summary = text.index("Professional Summary")
    experience = text.index("Professional Experience")
    projects = text.index("Selected Projects")
    education = text.index("Education")
    assert summary < experience < projects < education


def test_academic_cv_has_no_two_page_cap_and_lists_a_publication(inventory, tmp_path: Path):
    pdf, text = _render_pdf(inventory, "academic_cv", tmp_path / "cv")
    assert pdf_page_count(pdf) >= 2
    assert "Publications" in text
    assert "University of Tennessee" in text


def test_cover_letter_is_one_page(inventory, tmp_path: Path):
    spec = load_application(inventory.root / "examples" / "application.example.yaml")
    output = tmp_path / "letter out"
    generate_application(inventory, spec, output, compile_pdf=True)
    pdf = output / "cover_letter.pdf"
    assert pdf_page_count(pdf) == 1
    text = pdf_text(pdf)
    assert "Example Company" in text
    assert "Staff Data Engineer" in text
    assert "jngrant@" not in text
