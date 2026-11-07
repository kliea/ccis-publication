# Which OpenAlex author records match the roster?

Type: research
Label: wayfinder:research
Status: resolved
Blocked by:
Assignee: research-agent

## Question

For each researcher on the [roster](../roster.md), what OpenAlex author candidates exist, and which names are unambiguous?

Report candidates from the OpenAlex API: display name, author ID, ORCID, works count, and institutions. Use Caraga State University only as a hint when several records exist. Mark each name as one of:

- unambiguous — one candidate is clearly that researcher
- split — more than one record may be the same person
- collision — the name hit looks like a different person or a different institution
- miss — no candidate

Do not decide the binding rule. That is a later ticket. Cite OpenAlex docs and the API requests you ran.

## Comments

## Answer

On 2026-11-06 the authors search returned 37 unambiguous names, 5 splits, 1 collision, and 6 misses. The full table is in [01-author-matches.md](../research/01-author-matches.md).
