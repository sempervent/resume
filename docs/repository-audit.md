# Repository audit

Date of inspection: 2026-11-24. Branch inspected: `develop` at `f088152` ("updates for 2026"). Remote: `git@github.com:sempervent/resume`. Default branch: `develop`. `origin/master` exists and is behind `develop`.

## What was here

The repository was a sequence of hand-written LaTeX résumés and CVs from 2019 through 2026, plus `experience.txt`, `bibliography.bib`, and a résumé template. There was no generator, test suite, lockfile, or license file.

The newest résumé is `2026/2026-jng-revamped.tex`, committed in `f088152`. It is the baseline. `2026/2026-jng-cv.tex` is the longer CV from the same period and still uses the older macro style. `experience.txt` is older: its Data Engineer entry still says "Present," and it has no Bold Penguin role and no architect title.

A local untracked `2024/` directory and `out/` build directory were left untracked. They were not added to this branch.

## Authoritative choices

- Employment facts that the 2026 résumé and `experience.txt` both support use the résumé title and the more precise month from `experience.txt` when the month does not contradict the year.
- `2026/bibliography.bib` is the publication source. It has 19 entries. Earlier bibliographies contain `baxter2012field2`, a duplicate of `baxter2012field` with a broken author list, and `peluso2024environmental`, a duplicate of `PELUSO2024103303`. Those duplicates were not copied into `data/publications.bib`.
- Profile summaries are new framing over those sources. They do not add employers, tools, or numbers.

## Conflicts

| topic | sources | resolution |
| --- | --- | --- |
| ORNL data-engineer end date | `experience.txt` says June 2019–Present. 2026 résumés say Data Engineer 2019–2022 and Geospatial Systems Architect 2023–Present. | Split roles, as in the 2026 résumé. Architect start month is unknown. Data-engineer end month is unknown. |
| 2018–2022 compression | `2025/2025-jng-1pg.tex` labels 2018–2022 as one Data Engineer job. | Not used. Subcontractor 2018–2019 and Data Engineer 2019–2022 stay separate. |
| Data scientist title | `experience.txt`: Data Scientist II, October 2018–June 2019. 2026 résumés: Data Scientist II Subcontractor, 2018–2019. | Longer title, months from `experience.txt`. |
| Graduate title | `experience.txt`: Graduate Research Associate, July 2014–May 2016. 2026 résumés: Graduate Research Assistant, 2014–2016. | Résumé title, months from `experience.txt`. |
| Microbial Insights title | `experience.txt`: Bioinformatician. 2026 résumés add project manager and technical sales. | Longer 2026 title. Months August 2016–February 2018 from `experience.txt`. |
| 2018 contract employers | `experience.txt`: REsurety (Feb–Aug 2018) and DC Energy (Aug–Oct 2018). 2026 résumés fold contract work into Specrabella for 2018, including a Leaflet/Shiny/Snowflake energy application that `experience.txt` assigns to REsurety. | Three records. The map application stays on REsurety and is `review_required`. Specrabella keeps consulting and PostgreSQL statements that are not the same sentence. |
| Prefect migration leadership | 2026 CV: "Supervised a team effort." Revamped résumé: "Led migration." | Revamped wording. No team size. |
| Stacy's Greenhouses | Only in `experience.txt` (Lead Merchandiser, 2008–2012). | Preserved, not rendered. |
| Scala | Skill line on `2026/2026-jng-cv.tex` only. | Not added. The revamped skill list is the one in `data/skills.yaml`. |
| GCP, Azure, NiFi, Slurm, Spark, FastAPI, Django, Electron | Listed on the 2026 skill tables. Most have no matching employment bullet. Spark and Hadoop are closer: Hadoop is in the WSTAMP bullet. | Kept in the skill inventory because the owner published them. They are not treated as demonstrated project experience in the audit below. |

## Duplication on the current ORNL role

`2026/2026-jng-cv.tex` repeats GeoParquet warehousing and Prefect raster ingestion across several bullets. The revamped résumé already merges much of that. The inventory keeps one storage statement, one raster/vector pipeline statement, one spatial-database statement, and one clock-drift time-series statement from the CV that the revamped file does not spell out.

## Claims that stay qualitative

No source in this repository gives a data volume, workflow count, team size, cost delta, throughput, or user count. Achievement `metrics` lists are empty on purpose. "Improved consistency," "high-load," and "operational" are the owner's qualitative words and are kept where the 2026 résumé uses them. They are not backed by a number.

The parcel-monitoring bullet in the published résumé uses a sensitivity adjective. The generated statement names the stack and the tracking application without that adjective, and `ornl-parcel-monitoring` is `review_required`.

`ornl-covid-tracking` says distinguished recognition because both `experience.txt` and the revamped résumé say that. The award name is not in the source, so none is added.

## Stale or commercial-unfit detail

Laboratory methods, species lists, and the retail merchandising job are kept in the inventory. Commercial profiles do not render the pre-2016 laboratory roles or Stacy's. The academic CV renders the laboratory roles and the species list that the 2026 CV already published. It does not render Stacy's.

`clxns/id.tex` is an invention-disclosure list. It makes broader claims for personal projects (distributed systems, trading, blockchain) than the résumés do. Those claims were not copied into `data/projects.yaml`.

## Contact details

Historical TeX sources contained two residential street addresses, a mobile number, and two personal email addresses. Street addresses were removed from tracked `.tex` sources on this branch. Phone numbers and email addresses remain in those historical files and in committed PDFs. Git history still has the street addresses. See `docs/privacy.md`.

## Architecture decisions

- Python, uv, Pydantic, Jinja, and LaTeX. No web service, database, or required LLM.
- One inventory, six profiles. Dates and titles are read from employment records at render time.
- Publications are parsed from BibTeX with Pybtex so the academic CV does not need `biber`.
- Commercial page limit is enforced in tests with `pdfinfo`.
- Private contact is an optional gitignored file. Public builds do not need it.
- Application documents are refused unless the output path is outside the repo or gitignored.
- No `LICENSE` was added. The repository did not have one, and historical writing should not be licensed by this change.
- `@conference` entries are read as `@inproceedings` at parse time. The `.bib` file itself is unchanged aside from a comment about omitted duplicates.

## Unresolved questions

See `docs/achievement-verification.md` and the `review_required` flags. The highest-priority factual question is which 2018 employer owns the energy-informatics map application: REsurety, Specrabella, or both for different parts of the work.
