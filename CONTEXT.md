# Publication catalog

A catalog of scholarly works published in 2025 for a closed roster of researchers, shown as one table.

## Language

**Researcher**:
A person on the closed roster of 49 names. Cherry I. Tabada is one researcher.
_Avoid_: faculty, author, user

**Roster**:
The closed set of those 49 researchers. Sharing an institution does not add anyone.
_Avoid_: department, faculty list

**Publication**:
A scholarly work recorded as published in 2025. Researchers who share that work share one row. A different work is its own row, including when its title matches another.
_Avoid_: manuscript, submission, output

**Publication year**:
The year of publication recorded for a work. Only 2025 is in this catalog.
_Avoid_: submission year, acceptance year, presentation year

**Status**:
Published. Every publication in the catalog has this status.
_Avoid_: Submitted, Accepted, for Submission, Presented

**Author**:
A person named on a publication. A researcher is an author of their own publications. Coauthors who are not on the roster are still authors.
_Avoid_: researcher (when you mean any name on the byline)

**Author/s**:
Every author on a publication, listed together in that publication's row. A researcher's name is marked. An author who is not on the roster is unmarked.
_Avoid_: roster names only

**Row**:
The table's record of one publication. Researchers who share a publication share that row. Two different publications are two rows. A researcher with no publication has no row.
_Avoid_: one row per researcher, empty result

**Row order**:
Publications listed by title, A to Z, then by link, A to Z. A publication with no link follows one that has one, and two blank links use the earlier date. No. is the place of a row in that list, starting at 1.
_Avoid_: newest first, by researcher

**Snapshot**:
The saved set of publications the table shows. Opening the table does not ask OpenAlex again.
_Avoid_: live read

**Bound record**:
An OpenAlex author record that counts for a researcher. It is the one clear name match, an extra record that lists Caraga State University, or a middle-name expansion that lists no other university.
_Avoid_: every name hit, one record only

**Unmatched researcher**:
A researcher with no bound record. Nothing of theirs enters the snapshot.
_Avoid_: miss, collision

**Unchecked researcher**:
A researcher whose only author search kept the middle initial and found nobody. The next refresh searches that name without the middle initial. A clear match is bound. Nobody found is then an unmatched researcher.
_Avoid_: unmatched researcher

**Publisher**:
The organization that issues the journal or conference.
_Avoid_: sponsor, funder

**Sponsor**:
An organization that funded the publication.
_Avoid_: publisher

**Database**:
The bibliographic database a publication is listed in. This catalog does not record one.
_Avoid_: OpenAlex

**Indexing**:
Membership of a publication in an indexing service such as Scopus or Web of Science. This catalog does not record one.
_Avoid_: crossref, indexed_in

**Ranking**:
A journal ranking or Journal Impact Factor. This catalog does not record one.
_Avoid_: citedness, 2yr_mean_citedness

**Publication charge**:
The amount paid to publish, when that amount is recorded. Otherwise the advertised price.
_Avoid_: advertised price when an amount paid is recorded

**Site**:
The publication table, prepared as pages from the snapshot. A researcher with no publication is not listed.
_Avoid_: roster page, web app, account

**Detail**:
The full set of columns for one publication, opened over the ledger from its row.
_Avoid_: a second page

**Refresh**:
A request by whoever rebuilds and publishes the pages to replace the snapshot with a newer copy from OpenAlex and prepare the pages again. It is not on a schedule.
_Avoid_: live read, monthly update, account, named maintainer
