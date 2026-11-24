"""Compile LaTeX to PDF with the local TeX installation."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from career_docs.errors import CareerDocsError


def pdflatex_available() -> bool:
    return shutil.which("pdflatex") is not None


def compile_latex(tex_path: Path) -> Path:
    if not pdflatex_available():
        raise CareerDocsError(
            "pdflatex is not on PATH. Install the TeX packages listed in the README "
            "or build with the Docker image."
        )
    command = ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", tex_path.name]
    for _ in range(2):
        completed = subprocess.run(
            command,
            cwd=tex_path.parent,
            capture_output=True,
            text=True,
            check=False,
        )
        if completed.returncode != 0:
            log_path = tex_path.with_suffix(".log")
            detail = ""
            if log_path.is_file():
                lines = log_path.read_text(encoding="utf-8", errors="replace").splitlines()
                detail = "\n".join(lines[-40:])
            raise CareerDocsError(
                f"pdflatex failed for {tex_path.name} (exit {completed.returncode}).\n{detail}"
            )
    pdf_path = tex_path.with_suffix(".pdf")
    if not pdf_path.is_file() or pdf_path.stat().st_size == 0:
        raise CareerDocsError(f"pdflatex did not produce {pdf_path.name}")
    return pdf_path


def pdf_page_count(pdf_path: Path) -> int:
    if shutil.which("pdfinfo") is None:
        raise CareerDocsError("pdfinfo is not on PATH (install poppler).")
    completed = subprocess.run(
        ["pdfinfo", str(pdf_path)],
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise CareerDocsError(completed.stderr.strip() or f"pdfinfo failed for {pdf_path}")
    for line in completed.stdout.splitlines():
        if line.startswith("Pages:"):
            return int(line.split(":", 1)[1].strip())
    raise CareerDocsError(f"pdfinfo did not report a page count for {pdf_path}")


def pdf_text(pdf_path: Path) -> str:
    if shutil.which("pdftotext") is None:
        raise CareerDocsError("pdftotext is not on PATH (install poppler).")
    completed = subprocess.run(
        ["pdftotext", "-layout", str(pdf_path), "-"],
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise CareerDocsError(completed.stderr.strip() or f"pdftotext failed for {pdf_path}")
    return completed.stdout
