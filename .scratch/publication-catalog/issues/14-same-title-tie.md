# What breaks a tie when two titles match?

Type: grilling
Label: wayfinder:grilling
Status: resolved
Blocked by:
Assignee: wayfinder

## Question

The ledger lists publications by title, A to Z. Two publications can share a title. What decides which of those rows comes first, so No. stays the same from one reading of the snapshot to the next?

Invoke grilling and domain-modeling.

## Answer

The user chose the link. A paper shared by researchers is one row. Two different papers are two rows, including when the titles match. Those rows are ordered by the link, A to Z. A paper with no link comes after a paper that has one. If both links are blank, the earlier date comes first. No. is the place in that order.

**Publication**, **Row**, and **Row order** are locked in `CONTEXT.md`.

## Comments

The user said not to duplicate the publication row. The existing rule is already one publication, one row. The open point is what makes two records the same publication when the titles match.

The user added: if the publication has the same researchers, that is one publication. Abao and Abalorio sharing one paper counts as one. That matches the locked row rule. Still open: two different papers that use the same title.

The user then said: one row if both researchers share the paper; two rows if they do not. **Publication** and **Row** in `CONTEXT.md` now say a different work is its own row when the titles match. Still open: which of those two rows comes first.
