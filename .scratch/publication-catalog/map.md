# Publication catalog for 2025

Label: wayfinder:map

## Destination

A spec for a website whose main view is one publication table for the closed roster. Each row is a publication: a scholarly work OpenAlex records with publication year 2025. Every row's status is Published. The website is built in a later effort, from that spec.

The spec is [SPEC.md](../../SPEC.md).

Display columns, in order:

No. | Author/s | Title | Journal / Conference | Sponsor / Publisher | Database | Indexing | Ranking / JIF | ISSN / ISBN | Status (Published) | Date | Publication Charge | Link / DOI

## Notes

Domain is the publication catalog in `CONTEXT.md`. Caraga State University is a hint when matching a researcher to OpenAlex, not a reason to change the roster.

Skills for later sessions: grilling and domain-modeling on grilling tickets; research tickets read OpenAlex's own docs and API.

This map plans. It does not build the website.

Tracker: local markdown. Child tickets are `.scratch/publication-catalog/issues/NN-<slug>.md`. `Blocked by:` lists ticket numbers. A ticket is unblocked when every ticket it lists is `resolved`. The frontier is the open, unblocked, unclaimed children, lowest number first. Claim by setting `Status: claimed` before any work.

No git commit exists yet, so research notes are files under `.scratch/publication-catalog/research/` rather than `research/<name>` branches.

## Decisions so far

- [Which table columns can OpenAlex fill for a 2025 publication?](issues/02-openalex-column-fields.md) — Database, Ranking / JIF, and Status have no direct field; ISBN has none either, while ISSN does.
- [Is a shared publication one row or one row per researcher?](issues/03-shared-publication-rows.md) — One publication is one row. Author/s is the full byline.
- [Which OpenAlex author records match the roster?](issues/01-openalex-author-matches.md) — 37 unambiguous, 5 split, 1 collision, 6 miss.
- [Where does a researcher with no 2025 publication appear?](issues/04-researcher-with-no-2025-publication.md) — Nowhere in the publication table. No empty result.
- [Does the table read OpenAlex live or from a snapshot?](issues/05-live-read-or-snapshot.md) — A stored snapshot. Opening the table does not ask OpenAlex again.
- [How is a researcher bound to OpenAlex author records?](issues/06-bind-researcher-to-openalex.md) — Clear name match, plus extra Caraga State University records and the Jaymer Mernilo expansion. Pangasinan and De La Salle hits stay unbound.
- [What does a column show when OpenAlex has no value for it?](issues/07-unfilled-column-cells.md) — Publisher then sponsors. Database, Indexing, Ranking / JIF, and ISBN stay blank. Status is Published. Charge is amount paid, else advertised price.
- [Are roster researchers marked in the Author/s cell?](issues/08-mark-roster-names-in-byline.md) — A researcher's name is marked. Other authors are unmarked.
- [Does the site list researchers who have no 2025 publication?](issues/09-roster-page-for-empty-researchers.md) — No. The site is the publication table alone.
- [When is the snapshot refreshed?](issues/10-snapshot-refresh.md) — When someone asks. No schedule.
- [What does the publication table look like?](issues/11-publication-table-prototype.md) — A ledger. Clicking a row opens that publication's detail in a modal.
- [What order are the publication rows in?](issues/12-publication-row-order.md) — Title A to Z. The date is a column, not the order.
- [Does a refresh re-search the four unchecked names?](issues/13-refresh-rechecks-unchecked-names.md) — Yes. The next refresh searches those four without the middle initial. A clear match is bound. Nobody found stays out.
- [What breaks a tie when two titles match?](issues/14-same-title-tie.md) — A shared paper is one row. Different papers stay two rows, ordered by the link A to Z, then the earlier date when both links are blank.
- [What does the spec assume the site is?](issues/15-stack-and-hosting.md) — A static site. The snapshot is built into the pages. A refresh rebuilds them. No account, and no particular host.
- [Who may start a refresh?](issues/16-who-may-refresh.md) — Whoever rebuilds and publishes the pages. No named role.

## Not yet specified

## Out of scope

- Statuses other than Published: Submitted, Accepted, for Submission, Presented. The catalog lists published works only.
- Publication years other than 2025.
- Anyone who is not on the closed roster.
- Building or deploying the website inside this map. The destination is the spec.
