# Joshua N. Grant

**Data & Software Systems Architect**

Cloud-Native Data Platforms | Distributed Systems | Geospatial Engineering

This repository is the public source for Joshua N. Grant's résumé profiles and the tool that generates them. One YAML inventory feeds five commercial résumés, an academic CV, Markdown and plain text, and private application packets.

## Quick start

```bash
uv sync
uv run career-docs validate
uv run career-docs build --all
```

PDFs land in `dist/<profile>/`. You need `pdflatex`, `pdftotext`, and `pdfinfo` locally, or use the container below. Public builds do not need a phone number or email address.

Profiles:

| id | document |
| --- | --- |
| `data_architect` | Data platform architecture |
| `staff_engineer` | Staff software engineering |
| `geospatial_architect` | Geospatial systems architecture |
| `platform_engineer` | Platform and delivery engineering |
| `scientific_software` | Scientific and research software |
| `academic_cv` | Full CV, including publications |

Commercial résumés are limited to two pages. The academic CV is not.

## Local development

Requirements: Python 3.12 (uv will provision it), `uv`, and a TeX install that provides `pdflatex` plus `geometry`, `hyperref`, and `lmodern`. Poppler provides `pdftotext` and `pdfinfo`.

```bash
uv sync
uv run ruff check src tests
uv run ruff format --check src tests
uv run pytest
make test
make build-all
```

Useful commands:

```bash
uv run career-docs profiles
uv run career-docs build --profile staff_engineer
uv run career-docs audit
uv run career-docs export-context --profile staff_engineer
```

`export-context` writes a Markdown brief for an external model. It omits private contact details.

To put a phone number or email on a local copy only:

```bash
cp config/private.example.yaml config/private.yaml
# edit config/private.yaml
uv run career-docs build --profile data_architect --contact
```

`config/private.yaml` is gitignored. Do not put a street address in it. The generator rejects that key.

## Container build

The image is the reference build environment. It bakes dependencies in at image build time and does not install packages on container start.

```bash
docker buildx bake
docker run --rm -v "$PWD/dist:/work/dist" career-docs:local build --all
docker run --rm career-docs:local validate
```

LaTeX packages in the image: `texlive-latex-base`, `texlive-latex-recommended`, `texlive-latex-extra`, `texlive-fonts-recommended`, and `lmodern`, plus `poppler-utils`. PDF bytes are reproducible only in the sense that the same inputs render the same document. This repository does not claim byte-identical PDF files across TeX versions.

## Canonical data

Edit YAML under `data/`. Profiles under `profiles/` only choose emphasis, order, and which records appear. They do not copy employment dates or titles.

| file | contents |
| --- | --- |
| `data/identity.yaml` | Name, headline, public location, public links |
| `data/experience.yaml` | Employment records |
| `data/achievements.yaml` | Sourced accomplishment statements |
| `data/skills.yaml` | Skill groups taken from the 2026 résumé |
| `data/projects.yaml` | Portfolio projects with maturity notes |
| `data/education.yaml` | Degrees |
| `data/summaries.yaml` | Profile summaries |
| `data/publications.bib` | Bibliography for the academic CV |

`uv run career-docs validate` checks identifiers, dates, profile references, and visibility. It exits nonzero on errors.

### Update an experience record

1. Edit the record in `data/experience.yaml`. Keep the stable `id`.
2. Add or revise achievements in `data/achievements.yaml`.
3. Point `achievement_ids` at those achievements.
4. Select the achievements from the profiles that should show them.
5. Run `uv run career-docs validate` and `uv run career-docs build --all`.

Every achievement needs a source path, a verification status, and a visibility value. Leave `metrics` empty unless a number is in a cited source. Do not invent volumes, savings, team sizes, or adoption figures. `review_required: true` means the statement can still render, and application manifests flag it for a human read.

Résumé statements already in this repository are owner-provided evidence. They are not independently verified employment records.

## Tailored résumé and cover letter

Copy `examples/application.example.yaml` to a gitignored path such as `private/application.yaml`. Use a fictional example only in Git. Real employer names belong in `private/`.

```bash
mkdir -p private
uv run career-docs application \
  --input private/application.yaml \
  --output-dir private/example-company
```

The command checks achievement and project ids, rejects private or restricted records, and writes:

- `resume.tex`, `resume.pdf`, `resume.md`, `resume.txt`
- `cover_letter.tex`, `cover_letter.pdf`, `cover_letter.md`, `cover_letter.txt`
- `manifest.yaml`

The manifest separates machine-checked ids from prose that still needs a human read. Nothing is submitted anywhere.

If `cover_letter.paragraphs` is empty, the letter is filled from a fixed template plus the selected achievement statements. A supplied paragraph list is rendered as written and marked for review. The workflow does not call an LLM.

An external model may draft the YAML. It must not edit `data/`. Prompts for that handoff are in `prompts/`. Repository rules for agents are in `AGENTS.md`.

## Privacy

Public profile builds use the city and region in `identity.yaml` and the public links there. Historical TeX files and their PDFs still contain personal contact details, and Git history still contains residential street addresses that were removed from the current TeX sources. See `docs/privacy.md`. Do not rewrite history unless the owner asks for that explicitly.

Application output is refused if the destination is inside this repository and not gitignored.

## Validation and tests

```bash
uv run career-docs validate
uv run career-docs audit
uv run pytest
```

Tests cover schema and reference checks, LaTeX escaping, Markdown and plain text, application manifests, invalid input, private-data exclusion, and PDF compilation when `pdflatex` is installed. Plain-text extraction is an ATS-oriented check. It is not a certification that every applicant-tracking system will parse the file.

## Layout

`src/career_docs/` is the generator. `templates/` holds Jinja templates. `schemas/` describes the Pydantic models as JSON Schema. `docs/` holds the repository audit, portfolio audit, achievement questions, and privacy notes. `archive/README.md` explains why historical résumés were left in place.

There is no license file. Historical content stays unlicensed until the owner chooses one. This change does not add a license.

## Further reading

- `docs/repository-audit.md`
- `docs/portfolio-audit.md`
- `docs/achievement-verification.md`
- `docs/privacy.md`
- `AGENTS.md`
