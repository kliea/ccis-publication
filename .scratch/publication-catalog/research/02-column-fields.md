# OpenAlex fields behind the 2025 publication columns

Checked against the current OpenAlex docs and one full work plus its source. This note names the JSON path or says there is no field. It does not decide what a cell should show when a value is missing.

## Docs

- Works entity: https://docs.openalex.org/api-entities/works (page dated 2 November 2026)
- Work object, every attribute: https://docs.openalex.org/api-entities/works/work-object (2 November 2026)
- Location object: https://docs.openalex.org/api-entities/works/work-object/location-object (23 October 2026)
- Authorship object: https://docs.openalex.org/api-entities/works/work-object/authorship-object (17 October 2026)
- Sources entity: https://docs.openalex.org/api-entities/sources (15 October 2026)
- Source object: https://docs.openalex.org/api-entities/sources/source-object (27 October 2026)

Requests used `User-Agent: research-publication/1.0 (mailto:research-publication@example.com)` and `mailto=research-publication@example.com`.

## Work fetched

Junrie B. Matias, OpenAlex author `A5075735598`, has works in 2025. `GET /works?filter=authorships.author.id:A5075735598,publication_year:2025` returned `meta.count` 11. Vicente A. Pitogo was not needed.

Sample work: `https://openalex.org/W4412036207`, `publication_year` 2025, fetched at `GET /works/W4412036207`.

Its primary source, fetched at `GET /sources/S23629721` because the work only embeds a short source:

- `display_name`: International Journal of Advanced Computer Science and Applications
- `type`: `journal`
- `host_organization_name`: Science and Information Organization

The same author filter’s list also includes 2025 works whose embedded `primary_location.source.type` is `conference` (`W4413095945`, `W4416183244`, `W7117408048`). Those were not the fully read payload.

## Column map

| Column | JSON path, or no field | What `W4412036207` and source `S23629721` contained |
| --- | --- | --- |
| Author/s | `authorships[].raw_author_name` and `authorships[].author.display_name` | Three authorships. Raw names: John Mark Correa (first), Rudolph Joshua Candare (middle), Junrie B. Matias (last, `A5075735598`). The first authorship’s `author` is null; the other two have `author.display_name`. |
| Title | `display_name`, identical to `title` | “Deep Reinforcement Learning Based Robotic Arm Control Simulation to Execute Object Reaching Task for Industrial Application” |
| Journal / Conference | `primary_location.source.display_name` and `primary_location.source.type` (`journal`, `conference`, `repository`, `book series`, `ebook platform`, and others). `primary_location.raw_source_name` is the venue string before source matching. | Display name above. `type` is `journal`. `raw_source_name` matches that journal name. |
| Sponsor / Publisher | Publisher: `primary_location.source.host_organization_name` and `primary_location.source.host_organization` (a publisher id, or a repository’s institution). Sponsor: `funders[]` and `awards[]`. These are different facts. `grants` is removed. | Publisher name “Science and Information Organization” (`P4310311819`). One funder: “Science Education Institute, Department of Science and Technology, Republic of the Philippines” (`F4320336394`). `awards` is `[]`. No `grants` key. |
| Database | no field | No `database` key on the work or the source. |
| Indexing | `indexed_in` on the work. Documented values: `arxiv`, `crossref`, `doaj`, `pubmed`. | `["crossref"]`. |
| Ranking / JIF | no field for Journal Impact Factor or a ranking score | No impact-factor key on the work or the source. See the note below for the numbers that were present and are not JIF. |
| ISSN / ISBN | ISSN: `primary_location.source.issn` and `primary_location.source.issn_l` (the full source repeats them on `issn`, `issn_l`, and `ids.issn`). ISBN: no field. | ISSN-L `2156-5570`. ISSNs `2156-5570` and `2158-107X`. No `isbn` key on the work, its `ids`, or the source. |
| Status | no field | No `status` key. Nearby values that are not a status column: `primary_location.is_published` true, `primary_location.version` `publishedVersion`, `type` `article`, `open_access.oa_status` `diamond`, `is_retracted` false. |
| Date | `publication_date` and `publication_year` | `2025-01-01` and `2025`. |
| Publication Charge | List price on the work: `apc_list` (`value`, `currency`, `value_usd`). Estimate of the amount paid: `apc_paid` (same shape). Source list price, separate object: `apc_usd` and `apc_prices`. | `apc_list` null, `apc_paid` null, `apc_usd` null, `apc_prices` `[]`. |
| Link / DOI | `doi` and `ids.doi`. The copy also has `primary_location.doi` and `primary_location.landing_page_url`. | Work `doi` and `ids.doi` are `https://doi.org/10.14569/ijacsa.2025.0160666`. `ids` has only `openalex` and `doi`. Location `doi` and `landing_page_url` are that same DOI URL. `primary_location.pdf_url` and `open_access.oa_url` are a publisher PDF URL. |

The embedded `primary_location.source` on the work includes `display_name`, `type`, `issn`, `issn_l`, `is_oa`, `is_in_doaj`, `is_core`, `listed_in`, and the host-organization fields. It does not include `apc_usd` or `summary_stats`. Those were read from `GET /sources/S23629721`. The work-object docs say source `summary_stats` used in a works filter is looked up at query time and is not stored on the work.

Also checked on this work, and not a display column: `biblio` is `{volume: "16", issue: "6", first_page: null, last_page: null}`. `corresponding_institution` is absent; `corresponding_institution_ids` is `["https://openalex.org/I210563421"]` and `corresponding_author_ids` is `[]`. `best_oa_location` is present.

## Easy to confuse

**Publisher versus funder.** The source’s `host_organization` is the publisher, or the institution that hosts a repository. `funders` and `awards` are who funded the work. Docs say `grants` was removed in favor of those two. On this work the publisher is Science and Information Organization and the funder is a Department of Science and Technology institute. Same work, different organizations, different id prefixes (`P…` and `F…`).

**APC list price versus amount paid.** `apc_list` is the journal’s advertised charge, not necessarily what was paid. A zero `apc_list.value` means a diamond-OA journal. `apc_paid` is OpenAlex’s best estimate of the charge actually paid: the article’s own OpenAPC figure when OpenAPC has it, otherwise the list price for gold and hybrid works. Nothing on the object says which of those two an `apc_paid` value came from. `apc_usd` / `apc_prices` live on the source and are that source’s list price. This work is `open_access.oa_status` `diamond`, and every APC field above is null or empty.

**ISSN versus ISBN.** Sources carry `issn` and `issn_l`. Works identify externally with `doi`, `mag`, `pmid`, and `pmcid`. The work-object page mentions an ISBN only as an internal hint used to link a chapter to its book, not as a returned attribute. This payload has ISSNs and no ISBN anywhere.

**Citation stats versus Journal Impact Factor versus Scopus or Web of Science.**

- Work citation stats are `cited_by_count` (1 on this work), `counts_by_year`, `cited_by_percentile_year`, `fwci` (0.4045), and `citation_normalized_percentile`. Those describe this work. They are not a journal impact factor and not membership in an index.
- The source’s `summary_stats.2yr_mean_citedness` is a different fact. The source-object page calls it “a journal impact factor-style measure” and defines it as the mean `cited_by_count` of the source’s works from this year and the two years before, excluding peer reviews. On `S23629721` it is about 2.327, with `h_index` 102 and `i10_index` 3125. That number is not Clarivate Journal Impact Factor. The work payload does not carry it.
- `indexed_in` is which registries index the work. Documented values are only `arxiv`, `crossref`, `doaj`, and `pubmed`. This work is `["crossref"]`. Scopus and Web of Science are not in that list.
- A source list is not an index. `listed_in`, `is_in_doaj`, `is_in_scielo`, and `is_core` say which lists include the journal. Docs say CWTS Core is the Leiden Ranking list and is not the Web of Science Core Collection. This source is `is_in_doaj` false, `is_core` true, `is_in_scielo` false, and `listed_in` `anvur-scientific`, `cwts-core`, `norway-1`, `poland-20`, `russia-white-list-3`, `vabb-shw`.
- `GET /source-lists` on 6 November 2026 returned 63 lists. None of the ids or display names is Scopus, Web of Science, Clarivate, JCR, SCImago, or Journal Impact Factor. `GET /source-lists/scopus` and `GET /source-lists/wos` returned 404. Some of the 63 lists are national rankings or point lists. That is list membership, not a JIF field.
