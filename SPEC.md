# Publication catalog

A static website whose only view is one table of scholarly works published in 2025. The table is prepared from a saved snapshot. Opening the site does not ask OpenAlex again.

The words in [CONTEXT.md](CONTEXT.md) are the language of this spec. The decisions behind it are indexed in [Publication catalog for 2025](.scratch/publication-catalog/map.md).

## Roster

The roster is the closed list of 49 researchers in [roster.md](.scratch/publication-catalog/roster.md). Cherry I. Tabada is one researcher. Sharing an institution does not add or remove a name. Caraga State University is a hint when matching a researcher to OpenAlex, not a reason to change the roster.

A researcher with no 2025 publication does not appear. The site has no roster page.

## Publication

A publication is a scholarly work OpenAlex records with publication year 2025. That year is the year on the work, not a submission, acceptance, or presentation year. Every publication's status is Published.

Researchers who share a work share one row. The Author/s cell lists the full byline, including authors who are not on the roster. Two different works are two rows, including when their titles match.

## Snapshot

The snapshot is the saved set of publications the table shows. It includes a 2025 work when at least one author on that work is a bound record for a researcher.

A researcher is bound to the one clear OpenAlex name match. On a split, also bind every extra record that lists Caraga State University, and bind Jaymer Mernilo Jayoma (`A5065766137`) because Mernilo expands the roster initial and that record lists no other university. Do not bind John Mark Correa at Pangasinan State University (`A5120346959`). Do not bind James V. Presbitero at De La Salle University (`A5049211925`).

An unmatched researcher adds nothing. The match table is [01-author-matches.md](.scratch/publication-catalog/research/01-author-matches.md).

## Columns

The columns are, in order:

No. | Author/s | Title | Journal / Conference | Sponsor / Publisher | Database | Indexing | Ranking / JIF | ISSN / ISBN | Status | Date | Publication Charge | Link / DOI

A blank cell stays blank. No column is dropped.

| Column | Cell |
| --- | --- |
| No. | The place of the row in the row order, starting at 1. |
| Author/s | The full byline from the work's authorships. A researcher's name is marked. An author who is not on the roster is unmarked. |
| Title | The work's title. |
| Journal / Conference | The primary source's display name. |
| Sponsor / Publisher | The publisher, then any sponsor names after a semicolon. One of them alone when the other is missing. Blank when both are missing. The publisher is the source's host organization. A sponsor is a funder of the work. |
| Database | Blank. OpenAlex is not this column. |
| Indexing | Blank. `indexed_in` is not this column. |
| Ranking / JIF | Blank. Citedness is not a ranking. |
| ISSN / ISBN | The ISSN. ISBN stays blank. |
| Status | Published. |
| Date | The publication date. The publication year when no full date is recorded. |
| Publication Charge | The amount paid when that amount is recorded. Otherwise the advertised price. Otherwise blank. The source's `apc_usd` is not this column. |
| Link / DOI | The work's DOI. |

Field notes for the builder are in [02-column-fields.md](.scratch/publication-catalog/research/02-column-fields.md).

## Row order

Rows are ordered by title, A to Z, then by link, A to Z. A publication with no link follows one that has one. When both links are blank, the earlier date comes first. The date does not order the rest of the table.

## Screen

The site is one ledger: a wide table of those columns. Clicking a row opens that publication's detail over the table. The detail shows the same columns for that one publication. Close, the backdrop, and Escape dismiss it. Clicking a link in the row does not open the detail.

Roster names in the Author/s cell are marked in bold. Other authors are not.

The chosen screen is variant A of [publication-table.html](.scratch/publication-catalog/prototype/publication-table.html). That file is a throwaway prototype. Its sample rows and its provisional date-then-title order are not this spec.

## Refresh

A refresh happens when someone asks. There is no schedule. Whoever rebuilds and publishes the pages may start it. The spec names no role and no account. Any host that serves the built files is enough.

A refresh replaces the snapshot with a newer copy from OpenAlex and prepares the pages again. The same binding rule applies.

The next refresh also searches these four researchers without the middle initial: Cherry I. Tabada, Jessie Lynde M. Poralan, Junward B. Megullas, and Fritzie T. Nuez. Their earlier search kept the middle initial and found nobody. A clear match is bound. Nobody found stays out, and that researcher is then unmatched. Later refreshes do not repeat this special search.

Mary Pilar J. Barber and Robert Lee M. Bawiga were already searched both with and without the middle initial. They are not part of that special search.

## Out of scope

- Statuses other than Published: Submitted, Accepted, for Submission, and Presented.
- Publication years other than 2025.
- Anyone who is not on the roster.
- A roster page, an account, a named maintainer, and a scheduled refresh.
- Building or deploying the website. That is a later effort, done from this spec.
