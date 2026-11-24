from __future__ import annotations

from dataclasses import replace

import pytest

from career_docs.models import Visibility
from career_docs.render import build_view
from career_docs.textutil import latex_escape
from career_docs.validate import error_issues, validate_inventory


def test_inventory_has_no_validation_errors(inventory):
    errors = error_issues(validate_inventory(inventory))
    assert errors == []


def test_ids_are_unique(inventory):
    for label, values in (
        ("employment", [item.id for item in inventory.employment]),
        ("achievement", [item.id for item in inventory.achievements]),
        ("project", [item.id for item in inventory.projects]),
        ("profile", [item.id for item in inventory.profiles]),
    ):
        assert len(values) == len(set(values)), label


def test_employment_dates_are_ordered(inventory):
    for record in inventory.employment:
        if record.end is not None:
            assert record.start.year <= record.end.year


def test_profile_achievement_refs_resolve(inventory):
    achievements = inventory.achievement_map()
    for profile in inventory.profiles:
        for role in profile.roles:
            for achievement_id in role.achievement_ids:
                assert achievements[achievement_id].employment_id == role.employment_id


def test_commercial_profiles_share_canonical_dates(inventory):
    bold = inventory.employment_map()["bold-penguin-2022"]
    for profile in inventory.profiles:
        if profile.document_kind != "resume":
            continue
        view = build_view(inventory, profile)
        role = next(item for item in view.roles if "Bold Penguin" in item.organization)
        assert role.dates == "2022–2023"
        assert role.title == bold.title


def test_public_profiles_do_not_select_restricted_projects(inventory):
    projects = inventory.project_map()
    for profile in inventory.profiles:
        for project_id in profile.project_ids:
            assert projects[project_id].visibility == Visibility.public


def test_restricted_achievement_is_rejected(inventory):
    source = inventory.achievements[0]
    restricted = source.model_copy(
        update={
            "id": "restricted-example",
            "visibility": Visibility.restricted,
            "statement": "Not for publication.",
        }
    )
    cloned = replace(inventory, achievements=[*inventory.achievements, restricted])
    profile = cloned.profile_map()["data_architect"]
    with pytest.raises(Exception, match="restricted-example"):
        build_view(cloned, profile, achievement_ids=["restricted-example"])


def test_latex_escape_handles_specials():
    assert latex_escape(r"A & B % C $ # _ {x} ~ ^") == (
        r"A \& B \% C \$ \# \_ \{x\} \textasciitilde{} \textasciicircum{}"
    )
    assert "\\" in latex_escape("\\path")


def test_no_placeholder_metrics_in_statements(inventory):
    for achievement in inventory.achievements:
        assert achievement.metrics == []
        assert "TODO" not in achievement.statement
        assert "TBD" not in achievement.statement


def test_stacys_is_preserved_and_unselected(inventory):
    assert inventory.employment_map()["stacys-2008"].featured is False
    for profile in inventory.profiles:
        assert all(role.employment_id != "stacys-2008" for role in profile.roles)
