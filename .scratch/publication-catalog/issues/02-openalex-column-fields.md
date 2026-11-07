# Which table columns can OpenAlex fill for a 2025 publication?

Type: research
Label: wayfinder:research
Status: resolved
Blocked by:
Assignee: research-agent

## Question

For a publication (OpenAlex work with publication year 2025), which display column has a direct OpenAlex field, and which has none?

Columns, in order: Author/s, Title, Journal / Conference, Sponsor / Publisher, Database, Indexing, Ranking / JIF, ISSN / ISBN, Status, Date, Publication Charge, Link / DOI.

For each column, name the JSON path on a work or its source, or say there is no field. Call out fields that are easy to confuse with the column: publisher versus funder, list price versus amount paid for the publication charge, ISSN versus ISBN, and OpenAlex citation stats versus Journal Impact Factor or an index such as Scopus or Web of Science.

Do not decide what the cell should show when a field is missing. Cite the current OpenAlex works and sources docs, plus one real API payload for a 2025 work if one exists for a roster researcher.

## Comments

## Answer

For a 2025 OpenAlex work, Author/s, Title, Journal / Conference, Date, and Link / DOI have direct fields (`authorships`, `display_name`/`title`, `primary_location.source.display_name` plus `source.type`, `publication_date`/`publication_year`, and `doi`). Sponsor / Publisher is two different fields (`primary_location.source.host_organization_name` for the publisher, `funders` and `awards` for a sponsor). Indexing is `indexed_in` (documented values: arxiv, crossref, doaj, pubmed). ISSN is `primary_location.source.issn` / `issn_l`. Publication Charge is `apc_list` (list price) versus `apc_paid` (estimated amount paid), which are also different from the source’s `apc_usd`. Database, Ranking / JIF, Status, and ISBN have no direct field; `summary_stats.2yr_mean_citedness` is not Journal Impact Factor, and neither it nor `indexed_in` is Scopus or Web of Science. Sample: Junrie B. Matias, work `W4412036207`, `publication_year` 2025. Findings: [02-column-fields.md](../research/02-column-fields.md).
