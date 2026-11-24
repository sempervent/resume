# Portfolio audit

Inspection date: 2026-11-24, using the public GitHub API for `sempervent` and README text. Projects were not executed. A repository existing is not treated as a production deployment.

Private repositories were not cloned. `cosmic-architect` and `mythinc-cardgame` are private. Their code is not described here.

## Selected for résumés

| id | where it appears | why |
| --- | --- | --- |
| `parqonaut` | All commercial profiles and the CV | Strongest public data-infrastructure project. Rust workspace, CLI (`prqnt`), HTTP API, tests, fuzz/property tests mentioned in the README, Docker, docs site, CI, and GitHub releases. Latest tag observed was v0.9.2. Main-branch README text also discusses v0.12.0 work; résumés cite the tag, not that draft. No GeoParquet claim: the README does not make one. No adoption claim. |
| `dots` | Staff, platform, academic CV | Public workstation/profile manager since 2019, with CI and releases through v1.13.3. Relevant to developer environments and automation. It is not a cloud platform. The upstream README contains a personal email address; that address is not copied into this repository's data files. |
| `numbrane` | Staff, scientific software, academic CV | Polyglot computational art system (Python, Rust, TypeScript), CI, releases through v0.2.0. The README says it is not a generative-AI product. Résumé text calls it generative art, not scientific data infrastructure. |
| `syncscope-at-home` | Data, geospatial, platform, scientific, academic CV | Small public Compose scaffold (one observed commit, no release, no Actions workflow) that wires PostGIS and TimescaleDB around ORNL's OpenSAMPL. Included because the boundary is explicit: the demo is the owner's, OpenSAMPL is not. |

Two to four of these are selected per commercial profile. See `profiles/`.

## Evaluated and not selected by default

| project | evidence | why it is not a default résumé line |
| --- | --- | --- |
| streaming-parquet (`maw`) | Public MIT Rust CLI, tests in tree, no tags, no Actions. README throughput numbers are targets. | PARQONAUT already represents the Parquet work with releases and CI. The targets are not cited as measurements. The project remains selectable for a tailored packet. |
| paraclete | Public Rust service. README describes an HTTP API, auth, and Parquet scans. No tags and no Actions were present. Not executed. | Design-doc volume is ahead of release evidence. `review_required`. Select only if the owner wants it after a local run. |
| parqknife | Public Rust CLI, one commit, no CI, README still contains a generic clone URL. | Immature relative to PARQONAUT. |
| pygeopq | Public MIT repo whose tree is a README and license. One commit. | Stub. Not evidence of a GeoParquet library. |
| pyGARDEN | No public repository with that name. | Nothing to cite. |
| OpenSAMPL | Upstream is `ORNL/OpenSAMPL`, used as a submodule by `syncscope-at-home`. | Not the owner's product. The demo scaffold is the only related selection. |
| Cosmic Architect | Private `cosmic-architect` repository (metadata only: Python, AGPL-3.0, described as a web version). `2026/2026-jng-cv.tex` calls a pygame card game by this name. | Code was not reviewed. Visibility in the inventory is `restricted`, so public renders reject it. |
| cosmic-garden | Public TypeScript game, CI, one commit, no release. | A game prototype, not architecture evidence for these roles. |
| wildfire-smoke-risk-correlator | Public Python project with CI, Docker, and tests. Two commits, no release. | Not reviewed deeply enough to support a résumé claim beyond the repository description. |
| Where I've Been, Final Fantasy Football | Described on the 2026 résumé. No public repository found. | Academic CV only, marked `review_required`. Invention-disclosure language in `clxns/id.tex` is broader and was not used. |
| oil-price-checker, postgres-query-autopsy-tool, pg-dtw, and many other public repos | Present on the account. Several are single-commit or do not show releases. | Left out so the résumé does not treat repository count as a portfolio. |

## Ownership

Employer systems named in employment history (WSTAMP, NAERM-RTSA, Bold Penguin services, and OpenSAMPL) are not listed as personal projects. PARQONAUT, DOTS, and NUMBRANE are public repositories under the owner's account and are described as independent open source.
