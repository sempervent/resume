"""Plain-text helpers shared by validation and rendering."""

from __future__ import annotations

import re

from career_docs.models import Visibility

PLACEHOLDER_RE = re.compile(
    r"(\bTODO\b|\bTBD\b|\bFIXME\b|\bPLACEHOLDER\b|lorem ipsum|\[metric\]|<metric>|XX%)",
    re.IGNORECASE,
)

LATEX_SPECIALS = {
    "\\": r"\textbackslash{}",
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}

URL_SPECIALS = {
    "%": r"\%",
    "#": r"\#",
    "&": r"\&",
    "_": r"\_",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}


def latex_escape(value: str) -> str:
    return "".join(LATEX_SPECIALS.get(char, char) for char in value)


def latex_url(value: str) -> str:
    return "".join(URL_SPECIALS.get(char, char) for char in value)


def latex_to_text(value: str) -> str:
    text = value.replace(r"\&", "&")
    text = text.replace(r"\beta", "beta")
    text = text.replace(r"\alpha", "alpha")
    text = re.sub(r"\\textit\{([^{}]*)\}", r"\1", text)
    text = re.sub(r"\\emph\{([^{}]*)\}", r"\1", text)
    text = text.replace("$", "")
    text = re.sub(r"\\[a-zA-Z]+\s*", "", text)
    text = text.replace("{", "").replace("}", "")
    text = text.replace("--", "–")
    return re.sub(r"\s+", " ", text).strip()


def is_public(visibility: Visibility) -> bool:
    return visibility == Visibility.public


def word_count(text: str) -> int:
    return len(re.findall(r"[A-Za-z0-9][A-Za-z0-9’'+.-]*", text))
