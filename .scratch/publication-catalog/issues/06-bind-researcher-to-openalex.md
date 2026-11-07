# How is a researcher bound to OpenAlex author records?

Type: grilling
Label: wayfinder:grilling
Status: resolved
Blocked by: 01
Assignee: wayfinder

## Question

Given the match report from [Which OpenAlex author records match the roster?](./01-openalex-author-matches.md), what rule binds a researcher to one or more OpenAlex author IDs?

The answer must cover a split, a collision, and a miss: which records count, and what the spec does with a researcher who still has no safe match.

Invoke grilling and domain-modeling.

## Answer

"Continue" accepted rule A. A researcher is bound to the one clear name match. On a split, also bind every extra record that lists Caraga State University, and bind Jaymer Mernilo Jayoma (`A5065766137`) because Mernilo expands the roster initial and that record lists no other university. Do not bind John Mark Correa at Pangasinan State University (`A5120346959`). Do not bind James V. Presbitero at De La Salle University (`A5049211925`). A researcher with no bound record is unmatched, and nothing of theirs enters the snapshot. The match table is [01-author-matches.md](../research/01-author-matches.md).

Terms locked in `CONTEXT.md`: **Bound record**, **Unmatched researcher**.

## Comments
