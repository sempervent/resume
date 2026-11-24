# Achievement verification

These are the questions worth answering before the next résumé edit. Do not put a guessed number into `metrics`. Add a metric only after the source is identified, with `verification.sources` set and `review_required` cleared when the owner is satisfied.

None of the current achievement records include a quantitative metric. That is intentional.

## Priority questions

1. `bold-penguin-prefect-migration` and `bold-penguin-delivery-standardization`.
   How many engineering teams or services used the shared Prefect and CI/CD path? The résumés say "across engineering teams" and do not give a count. A count would show scope of technical leadership without changing the title. Source: internal Bold Penguin design notes or the owner's recollection. Likely not public in detail. Question: How many teams or production services adopted the Prefect 2 workflows or the shared GitHub Actions path, and can that number be stated publicly?

2. `bold-penguin-api-message-queue` and `bold-penguin-document-microservices`.
   The résumé says "high-load" and, in the CV, improved performance, with no throughput or latency figure. Source: service dashboards or load-test notes. Treat production volumes as non-public unless Bold Penguin agrees. Question: What document volume, queue depth, or latency change can be described publicly, if any?

3. `bold-penguin-runtime-routing`.
   Question: Roughly how many workflow types, or what range of input sizes, drove the EC2 versus Fargate choice? Is a range public?

4. `ornl-geoparquet-platform` and `ornl-spatial-database-analytics`.
   Question: What raster collection size, dataset count, or geometry count can be stated in a public résumé? Possible sources are project design docs or published technical reports such as the geospatial workflow report in `data/publications.bib`. Confirm public releasability before adding a figure. Do not use an internal-only volume.

5. `ornl-raster-vector-pipelines` and `ornl-airflow-k8s-migration`.
   Question: How many production workflows or scheduled pipelines were in the Airflow or Prefect estates you operated, and how often did they deploy? Deployment frequency and pipeline count are the useful pair. Mark anything internal as not for the public PDF.

6. `ornl-naerm-services`.
   Question: How many data products or partner exchanges did the OpenAPI services support? Confirm the NAERM-RTSA name is still appropriate on a commercial résumé.

7. `ornl-sqa-and-data-council`.
   Question: Was the SQA role a chair of a standing board with a defined membership, and for which dates? A membership count is optional. Do not describe this as laboratory-wide authority; the source limits it to the division board and Data Council participation.

8. `ornl-covid-tracking`.
   Question: What was the name of the recognition, and should it appear? The sources say "distinguished recognition" and do not name it.

9. `ornl-parcel-monitoring`.
   Question: Is the public wording, without the sensitivity adjective used in the 2026 TeX, acceptable? Are Kafka, TimescaleDB, and AWS accurate and releasable together?

10. `ornl-llm-data-discovery`.
    Question: Is the retrieval-augmented workflow public, and was it a prototype or an operational tool? Do not add a user count unless you have one you can publish.

11. `resurety-energy-application` and the Specrabella records.
    Question: Which employer should carry the map-based energy application: REsurety, Specrabella, or both for different deliverables? This is the main factual conflict in the inventory.

12. `parqonaut`.
    Question: Should résumés move from "releases through v0.9.2" to a newer tag once that tag exists? Do not cite v0.12.0 until it is a GitHub release. Are there external users or downstream dependents you can name?

13. Open-source maintenance.
    Question: For DOTS and NUMBRANE, is there a user or install count you actually know? Stars on 2026-11-24 were not evidence of adoption (DOTS had 1, the others 0). Leave adoption unstated if you do not have a source.

## Explicitly not requested

Team sizes, budgets, and clearance status are not in the sources. Do not add them to fill space. GCP and Azure are on the skill list because the 2026 résumé lists them; there is no achievement that shows a GCP or Azure system. Remove them from `data/skills.yaml` if that listing overstates hands-on use.
