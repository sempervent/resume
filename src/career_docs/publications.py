"""Parse publications.bib without requiring a LaTeX bibliography run."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from pybtex.database import parse_string

from career_docs.errors import CareerDocsError
from career_docs.textutil import latex_to_text


@dataclass(frozen=True)
class Publication:
    key: str
    year: int
    authors: str
    title: str
    title_text: str
    venue: str
    venue_text: str
    url: str


def load_publications(path: Path) -> list[Publication]:
    if not path.is_file():
        raise CareerDocsError(f"Missing bibliography: {path}")
    raw = path.read_text(encoding="utf-8")
    normalized = raw.replace("@conference{", "@inproceedings{")
    try:
        bibliography = parse_string(normalized, bib_format="bibtex")
    except Exception as exc:
        raise CareerDocsError(f"Could not parse {path.name}: {exc}") from exc

    publications: list[Publication] = []
    for key, entry in bibliography.entries.items():
        year_text = entry.fields.get("year", "").strip()
        if not year_text.isdigit():
            raise CareerDocsError(f"Publication {key} is missing a numeric year")
        people = entry.persons.get("author", [])
        authors = _format_authors(people)
        title = _clean_field(entry.fields.get("title", ""))
        venue = _clean_field(
            entry.fields.get("journal")
            or entry.fields.get("booktitle")
            or entry.fields.get("institution")
            or entry.fields.get("publisher")
            or entry.fields.get("organization")
            or ""
        )
        url = entry.fields.get("url", "").strip()
        publications.append(
            Publication(
                key=key,
                year=int(year_text),
                authors=authors,
                title=title,
                title_text=latex_to_text(title),
                venue=venue,
                venue_text=latex_to_text(venue),
                url=url,
            )
        )
    publications.sort(key=lambda item: (-item.year, item.key))
    return publications


def _clean_field(value: str) -> str:
    return " ".join(value.split())


def _format_name(person: object) -> str:
    first = " ".join([*person.first_names, *person.middle_names])  # type: ignore[attr-defined]
    last = " ".join(person.last_names)  # type: ignore[attr-defined]
    if first and last:
        return f"{first} {last}"
    return last or first


def _format_authors(people: list[object]) -> str:
    names = [_format_name(person) for person in people]
    names = [name for name in names if name]
    if not names:
        return ""
    if len(names) == 1:
        return names[0]
    if len(names) == 2:
        return f"{names[0]} and {names[1]}"
    return ", ".join(names[:-1]) + f", and {names[-1]}"
