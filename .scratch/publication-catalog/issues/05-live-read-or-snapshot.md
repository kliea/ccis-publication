# Does the table read OpenAlex live or from a snapshot?

Type: grilling
Label: wayfinder:grilling
Status: resolved
Blocked by:
Assignee: wayfinder

## Question

Does the spec's table read OpenAlex at request time, or show a stored snapshot of 2025 publications?

Invoke grilling and domain-modeling.

## Answer

The table shows a stored snapshot of 2025 publications. Opening the table does not ask OpenAlex again. The user chose A. When that snapshot is refreshed is a later ticket.

The **Snapshot** term is locked in `CONTEXT.md`.

## Comments
