from __future__ import annotations

from career_docs.render import build_view, render_templates
from career_docs.textutil import word_count

REQUIRED_HEADINGS = [
    "Professional Summary",
    "Technical Skills",
    "Professional Experience",
    "Selected Projects",
    "Education",
]


def test_markdown_and_text_keep_section_order(inventory):
    profile = inventory.profile_map()["staff_engineer"]
    view = build_view(inventory, profile)
    outputs = render_templates(inventory.root, view)
    for kind in ("md", "txt"):
        text = outputs[kind]
        positions = [text.index(heading) for heading in REQUIRED_HEADINGS]
        assert positions == sorted(positions)
        assert "Oak Ridge National Laboratory" in text
        assert "Bold Penguin" in text
        assert "Geospatial Systems Architect" in text
        assert "{{" not in text
        assert "{%" not in text


def test_plain_text_is_readable_without_markup(inventory):
    profile = inventory.profile_map()["data_architect"]
    text = render_templates(inventory.root, build_view(inventory, profile))["txt"]
    assert "Data & Software Systems Architect" in text
    assert "**" not in text
    assert "June 2019–2022" in text


def test_academic_cv_includes_publications_and_early_roles(inventory):
    profile = inventory.profile_map()["academic_cv"]
    text = render_templates(inventory.root, build_view(inventory, profile))["txt"]
    assert "Curriculum Vitae" in text
    assert "Publications" in text
    assert "Microbial Insights" in text
    assert "University of Tennessee" in text
    assert "Plant" in text or "Panicum" in text


def test_summary_wording_is_nonempty(inventory):
    for profile in inventory.profiles:
        view = build_view(inventory, profile)
        assert word_count(view.summary) > 40
        assert view.roles
        assert view.projects
