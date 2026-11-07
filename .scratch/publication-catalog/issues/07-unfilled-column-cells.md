# What does a column show when OpenAlex has no value for it?

Type: grilling
Label: wayfinder:grilling
Status: resolved
Blocked by: 02
Assignee: wayfinder

## Question

For each display column that [Which table columns can OpenAlex fill for a 2025 publication?](./02-openalex-column-fields.md) marks absent or ambiguous, what does the cell contain?

A direct field is used as-is. For the others, the answer is one of: a named OpenAlex substitute, blank, or the column dropped from the spec. Expected pressure points are Sponsor / Publisher, Database, Indexing, Ranking / JIF, and Publication Charge.

Invoke grilling and domain-modeling. Lock any column terms in `CONTEXT.md`.

## Answer

"Continue" accepted every recommended cell. Direct fields stay as they are: Author/s, Title, Journal / Conference, Date, ISSN, and Link / DOI.

- Sponsor / Publisher: publisher, then any sponsor names after a semicolon. One of them alone when the other is missing. Blank when both are missing.
- Database: blank. Column stays.
- Indexing: blank. Column stays. `indexed_in` is not this column.
- Ranking / JIF: blank. Column stays. Citedness is not a ranking.
- ISSN / ISBN: the ISSN. ISBN blank. Column stays.
- Status: Published.
- Publication charge: the amount paid when recorded, otherwise the advertised price, otherwise blank.

Terms locked in `CONTEXT.md`: **Publisher**, **Sponsor**, **Database**, **Indexing**, **Ranking**, **Publication charge**.

## Comments
