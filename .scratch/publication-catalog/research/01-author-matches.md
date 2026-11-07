# OpenAlex author matches for the roster

Verdicts below come from OpenAlex API responses fetched on 2026-11-06. They are not taken from the prior sample. Author IDs are the short form documented as `A` plus digits; the API `id` is `https://openalex.org/` plus that short form. ORCID values below are the path of the URL the API returned (`orcid` was null unless a URL is named). Institution names are `display_name` strings from `last_known_institutions` and `affiliations`. No IDs are merged.

## Sources

- Authors endpoint. [https://docs.openalex.org/api-entities/authors/author-object](https://docs.openalex.org/api-entities/authors/author-object) redirected, on this fetch, to [https://help.openalex.org/data/authors/](https://help.openalex.org/data/authors/). That page says the authors endpoint is `api.openalex.org/authors`, and it defines `id`, `display_name`, `orcid`, `works_count`, `cited_by_count`, `last_known_institutions`, and `affiliations`. It also says free-text name search uses the `search` parameter and that the `display_name.search` filter is deprecated.
- Search behavior. [https://docs.openalex.org/api-entities/authors/search-authors](https://docs.openalex.org/api-entities/authors/search-authors) redirected to [https://help.openalex.org/api/searching/](https://help.openalex.org/api/searching/). Author search covers `display_name` and `display_name_alternatives`. Words not separated by a boolean operator are treated as AND.

## Requests

Roster-name search, one name at a time, about 0.35 seconds apart. `per_page=5`. Every roster search returned `meta.count` of 0, 1, 2, or 3, so the page held the full result.

```text
GET https://api.openalex.org/authors?search={roster display name}&per_page=5&mailto=research-publication@example.com&select=id,display_name,orcid,works_count,cited_by_count,last_known_institutions,affiliations,relevance_score
User-Agent: mailto:research-publication@example.com
```

The search parameter ANDs the tokens. A roster string that includes a middle initial can miss a profile whose name omits that initial. Re-checking sample ID `A5136129512` showed this: `search=Junrie B. Matias` returned count 1 (`A5075735598` only), while `GET /authors/A5136129512` still returned `Junrie Matias` at Caraga State University with 3 works. A second sequential pass dropped single-letter initials (`Junrie B. Matias` to `Junrie Matias`) and was completed for Cristopher C. Abalorio through Vicente A. Pitogo.

The next call, `search=James Presbitero`, and a later probe, returned HTTP 429. The body said the keyless daily budget for this IP was used up and resets at midnight UTC. `Retry-After` on the probe was 66886. These roster names were not searched again without the middle initial: James V. Presbitero, Mary Rose O. Raz, Dexter A. Romaguera, Jordylene G. Sagusay, Cherry I. Tabada, Jesterlyn Q. Timosan, Luisito I. Tabada, Kier Patrick A. Empang, Klinth Jerald L. Matugas, Jessie Lynde M. Poralan, Junward B. Megullas, Mary Abigail D. Soliva, Fritzie T. Nuez. Al Christian Plaza has no single-letter initial. Some profiles that omit an initial in `display_name` still matched the full roster string (Dexter A. Romaguera, Rudolph Joshua U. Candare, Hannah Faye A. Capoy, James Earl D. Cubillas). Junrie shows that this does not always happen.

Works calls, used only to read affiliation strings on an author already found:

- `GET /works?filter=author.id:A5049211925&per_page=5`
- `GET /works?filter=author.id:A5154439464&per_page=3`
- `GET /works?filter=author.id:A5136212287&per_page=5`
- `GET /works?filter=author.id:A5065766137&per_page=5`

Same `mailto` and User-Agent. Caraga State University is a hint only where more than one person-like record exists. It is not a reason to drop a sole name match, and it is not a binding rule.

## Counts

- unambiguous: 37
- split: 5
- collision: 1
- miss: 6

49 roster names. The four misses Mary Pilar J. Barber and Robert Lee M. Bawiga were empty on both the roster string and the initial-dropped string. Cherry I. Tabada, Jessie Lynde M. Poralan, Junward B. Megullas, and Fritzie T. Nuez were empty on the roster string only. The initial-dropped search for those four did not run.

## Roster table

| # | Roster name | Verdict | Candidate IDs | Chosen evidence |
| --- | --- | --- | --- | --- |
| 1 | Cristopher C. Abalorio | unambiguous | A5010125303 | A5010125303, display name Cristopher C. Abalorio, no ORCID, 23 works, 46 citations. Last known Caraga State University. Affiliations also include Emilio Aguinaldo College, Technological Institute of the Philippines-Quezon City, and ACLC College of Butuan City. The same search returns A5154439464, whose display name is the byline "Cristopher C. Abalorio, Ariel M. Sison, Ruji P. Medina, Gleen A. Dalaorao" (1 work, 0 citations, no institution). That hit is not a second profile of this person. |
| 2 | Roland P. Abao | unambiguous | A5047149755 | One hit. A5047149755, Roland P. Abao, ORCID https://orcid.org/0000-0001-6281-3822, 17 works, 59 citations. Last known Caraga State University. Affiliations: Caraga State University (2019, 2021, 2025, 2026), Ateneo de Manila University (2021–2023), Mindanao State University – Iligan Institute of Technology (2018). |
| 3 | Jayrhom R. Almonteros | unambiguous | A5069971657 | One hit. A5069971657, Jayrhom R. Almonteros, ORCID https://orcid.org/0000-0002-6077-2710, 18 works, 27 citations. Last known and affiliated: Caraga State University (2022, 2024–2026). |
| 4 | Glaicel A. Araneta | unambiguous | A5119335978 | One hit. A5119335978, display name Glaicel Anania ARANETA, no ORCID, 2 works, 0 citations. Last known and affiliated: Caraga State University (2025–2026). The middle initial A matches Anania on this same record. |
| 5 | Jenelyn R. Asis | unambiguous | A5120905689 | One hit. A5120905689, Jenelyn R. Asis, no ORCID, 6 works, 1 citation. Last known and affiliated: Caraga State University (2025–2026). |
| 6 | Mary Pilar J. Barber | miss | none | `search=Mary Pilar J. Barber` and `search=Mary Pilar Barber` both returned count 0. |
| 7 | Robert Lee M. Bawiga | miss | none | `search=Robert Lee M. Bawiga` and `search=Robert Lee Bawiga` both returned count 0. |
| 8 | Nathan Kit A. Berro | unambiguous | A5114984484 | One hit. A5114984484, Nathan Kit A. Berro, ORCID https://orcid.org/0009-0008-8755-3199, 6 works, 13 citations. Last known and affiliated: Caraga State University (2024–2026). |
| 9 | Ronnel O. Cacho | unambiguous | A5083660397 | One hit. A5083660397, Ronnel O. Cacho, no ORCID, 6 works, 1 citation. Last known and affiliated: Caraga State University (2025–2026). |
| 10 | Rudolph Joshua U. Candare | unambiguous | A5084287731 | One hit. A5084287731, display name Rudolph Joshua Candare, no ORCID, 16 works, 16 citations. Last known and affiliated: Caraga State University (2016, 2020, 2022, 2024–2026). |
| 11 | Hannah Faye A. Capoy | unambiguous | A5017749693 | One hit. A5017749693, display name Hannah Faye Capoy, no ORCID, 3 works, 3 citations. Last known Caraga State University (2026). Also affiliated: UM Digos College (2019). |
| 12 | John Mark B. Correa | split | A5120889243, A5120346959 | Roster search returned only A5120889243, John Mark B. Correa, no ORCID, 1 work, 0 citations, Caraga State University (2025). Dropping the initial also returned A5120346959, John Mark Correa, no ORCID, 2 works, 0 citations, last known Pangasinan State University (2025). The second record may be the same person. Caraga State University is only a hint between them. |
| 13 | James Earl D. Cubillas | unambiguous | A5058737285 | One hit. A5058737285, display name James Earl Cubillas, ORCID https://orcid.org/0000-0002-1767-9094, 17 works, 24 citations. Last known and affiliated: Caraga State University (2016, 2022, 2024–2025). |
| 14 | John Michael F. Cutamora | unambiguous | A5120398403 | One hit. A5120398403, John Michael F. Cutamora, no ORCID, 5 works, 2 citations. Last known and affiliated: Caraga State University (2025–2026). |
| 15 | Gleen A. Dalaorao | unambiguous | A5079210661 | A5079210661, Gleen A. Dalaorao, no ORCID, 14 works, 54 citations. Last known Caraga State University (2022, 2024–2026). Also affiliated: Emilio Aguinaldo College (2022), Technological Institute of the Philippines-Quezon City (2019, 2022), Technological Institute of the Philippines (2020). The same search returns the byline record A5154439464 (see Cristopher C. Abalorio). That hit is not a second profile of Gleen. |
| 16 | Jayson C. Dollete | unambiguous | A5121232067 | One hit. A5121232067, Jayson C. Dollete, no ORCID, 6 works, 0 citations. Last known and affiliated: Caraga State University (2025–2026). |
| 17 | Paulo A. Duga | unambiguous | A5116295811 | One hit. A5116295811, Paulo A. Duga, no ORCID, 3 works, 3 citations. Last known and affiliated: Caraga State University (2024–2026). |
| 18 | Riah E. Encarnacion | split | A5011650373, A5120888696, A5159661622 | Three hits, all last known at Caraga State University, none with an ORCID. A5011650373, display name Riah Elcullada Encarnacion, 28 works, 173 citations. Affiliations: University of Nizwa (2021), Surigao del Norte State University (2024), Caraga State University (2025). A5120888696, Riah E. Encarnacion, 5 works, 1 citation, Caraga State University (2025–2026). A5159661622, display name Riah E. Encarnacion Dit, 1 work, 0 citations, Caraga State University (2026). These may be the same person. Not merged. |
| 19 | John Binze B. Escol | unambiguous | A5092891555 | One hit. A5092891555, John Binze B. Escol, no ORCID, 3 works, 2 citations. Last known and affiliated: Caraga State University (2026). |
| 20 | Giovanni T. Esma | unambiguous | A5121194004 | One hit. A5121194004, Giovanni T. Esma, no ORCID, 4 works, 1 citation. Last known and affiliated: Caraga State University (2025). |
| 21 | Kent T. Espejon | unambiguous | A5094089741 | One hit. A5094089741, Kent T. Espejon, ORCID https://orcid.org/0009-0001-4536-6247, 7 works, 4 citations. Last known and affiliated: Caraga State University (2023–2026). |
| 22 | Clark Justine L. Gonzales | split | A5121242116, A5159636087 | Roster search returned only A5121242116, Clark Justine L. Gonzales, no ORCID, 2 works, 0 citations, Caraga State University (2025). Dropping the initial also returned A5159636087, Clark Justine Gonzales, no ORCID, 1 work, 0 citations, Caraga State University (2026). Both may be the same person. Not merged. |
| 23 | Edwin Manuel M. Jarlata | unambiguous | A5136212287 | `search=Edwin Manuel M. Jarlata` returned count 0. `search=Edwin Manuel Jarlata` returned one hit: A5136212287, Edwin Manuel Jarlata, no ORCID, 1 work, 1 citation, empty `last_known_institutions` and empty `affiliations`. That work is the 2025 title "Enhancing Student Record Searches at Caraga State University using Mistral 7B Model". Its authorship has empty raw affiliation strings and an empty institutions list. One name match, so the empty institution fields are a gap on the record, not a second person. |
| 24 | Jaymer M. Jayoma | split | A5067578352, A5065766137 | Roster search returned only A5067578352, Jaymer M. Jayoma, ORCID https://orcid.org/0000-0001-7063-2693, 34 works, 77 citations. Last known Caraga State University (2018–2026). Also affiliated: Technological Institute of the Philippines-Quezon City (2018). Dropping the initial also returned A5065766137, Jaymer Mernilo Jayoma, no ORCID, 1 work, 1 citation, no institution. That work is the 2011 title "Design and Implementation of Middleware Application for Solving Database Server Overloading", with empty raw affiliation strings. M. may expand to Mernilo, so the two records may be the same person. Not merged. |
| 25 | Junrie B. Matias | split | A5075735598, A5136129512 | Roster search returned only A5075735598, Junrie B. Matias, ORCID https://orcid.org/0000-0001-9638-4667, 37 works, 174 citations. Last known Caraga State University (2019–2022, 2024–2026). Also affiliated: Emilio Aguinaldo College (2022), Technological Institute of the Philippines-Quezon City (2018, 2022), Technological Institute of the Philippines (2018). Direct GET and `search=Junrie Matias` also return A5136129512, Junrie Matias, no ORCID, 3 works, 2 citations, Caraga State University (2026). Both may be the same person. Not merged. |
| 26 | Angel Lorraine M. Morales | unambiguous | A5159661252 | One hit. A5159661252, Angel Lorraine M. Morales, no ORCID, 1 work, 0 citations. Last known and affiliated: Caraga State University (2026). |
| 27 | Edsel Matt O. Morales | unambiguous | A5080108496 | One hit. A5080108496, Edsel Matt O. Morales, no ORCID, 16 works, 47 citations. Last known and affiliated: Caraga State University (2016–2017, 2019–2021, 2024–2026). |
| 28 | Elbert S. Moyon | unambiguous | A5070606721 | One hit. A5070606721, Elbert S. Moyon, ORCID https://orcid.org/0000-0002-1259-1624, 20 works, 44 citations. Last known and affiliated: Caraga State University (2020–2026). |
| 29 | Takeyasu V. Nakazato | unambiguous | A5051861067 | One hit. A5051861067, Takeyasu V. Nakazato, ORCID https://orcid.org/0009-0004-3199-7621, 9 works, 3 citations. Last known institutions are both Caraga State University (2024–2026) and Technological Institute of the Philippines (2025–2026). One record, not two profiles. |
| 30 | Maria Besa Joy M. Ortuyo | unambiguous | A5094188681 | One hit. A5094188681, Maria Besa Joy M. Ortuyo, no ORCID, 4 works, 0 citations. Last known and affiliated: Caraga State University (2024–2026). |
| 31 | Paolo L. Pacaldo | unambiguous | A5120349545 | Roster search returned one hit: A5120349545, Paolo L. Pacaldo, no ORCID, 6 works, 3 citations, Caraga State University (2025–2026). `search=Paolo Pacaldo` also returned A5121147432, Paolo S. Pacaldo, no ORCID, 1 work, 0 citations, Caraga State University (2025). The middle initial on that second record is S, not L, so it is a different person, not a second record of Paolo L. Pacaldo. |
| 32 | Mark Phil B. Pacot | unambiguous | A5024726538 | One hit. A5024726538, Mark Phil B. Pacot, ORCID https://orcid.org/0000-0003-2548-4059, 22 works, 32 citations. Last known Caraga State University (2017–2018, 2020, 2022–2026). Also affiliated: De La Salle University (2020, 2023, 2025). Initial-dropped search returned the same single ID. |
| 33 | Kimberly Ann B. Palaran | unambiguous | A5120349505 | One hit. A5120349505, Kimberly Ann B. Palaran, no ORCID, 5 works, 1 citation. Last known and affiliated: Caraga State University (2025–2026). |
| 34 | Joanna Victoria S. Pitao | unambiguous | A5094052604 | One hit. A5094052604, Joanna Victoria S. Pitao, no ORCID, 4 works, 7 citations. Last known and affiliated: Caraga State University (2024–2025). |
| 35 | Vicente A. Pitogo | unambiguous | A5056076342 | One hit. A5056076342, display name Vicente Aquino Pitogo, ORCID https://orcid.org/0000-0002-2061-7521, 36 works, 99 citations. Last known Caraga State University (2018–2026). Also affiliated: De La Salle University (2018–2020, 2022), Asia-Europe Foundation (2025). `search=Vicente Pitogo` returned the same single ID. |
| 36 | James V. Presbitero | collision | A5049211925 | One hit. A5049211925, James V. Presbitero, no ORCID, 1 work, 4 citations. Last known De La Salle University (2018). The work is the 2018 title "Assessing compliance of Philippine state universities to the data privacy act of 2012". Raw affiliation string: "De La Salle University, Manila, Philippines". No Caraga State University institution on the record. The name matches; the institution does not. Initial-dropped search did not run. |
| 37 | Mary Rose O. Raz | unambiguous | A5120926324 | One roster-search hit. A5120926324, Mary Rose O. Raz, no ORCID, 5 works, 3 citations. Last known and affiliated: Caraga State University (2024–2026). Initial-dropped search did not run. |
| 38 | Dexter A. Romaguera | unambiguous | A5095934684 | One roster-search hit. A5095934684, display name Dexter Romaguera, no ORCID, 2 works, 16 citations. Last known and affiliated: Caraga State University (2024–2025). Initial-dropped search did not run. |
| 39 | Jordylene G. Sagusay | unambiguous | A5138715107 | One roster-search hit. A5138715107, Jordylene G. Sagusay, no ORCID, 1 work, 0 citations. Last known and affiliated: Caraga State University (2026). Initial-dropped search did not run. |
| 40 | Cherry I. Tabada | miss | none | `search=Cherry I. Tabada` returned count 0. Initial-dropped search did not run. |
| 41 | Jesterlyn Q. Timosan | unambiguous | A5023348383 | One roster-search hit. A5023348383, display name Jesterlyn Quibol Timosan, ORCID https://orcid.org/0000-0003-4425-2261, 9 works, 14 citations. Last known and affiliated: Caraga State University (2020, 2022, 2025–2026). Initial Q matches Quibol on this record. Initial-dropped search did not run. |
| 42 | Luisito I. Tabada | unambiguous | A5029531959 | One roster-search hit. A5029531959, Luisito I. Tabada, no ORCID, 2 works, 1 citation. Last known and affiliated: Caraga State University (2009, 2014). Initial-dropped search did not run. |
| 43 | Kier Patrick A. Empang | unambiguous | A5120631089 | One roster-search hit. A5120631089, Kier Patrick A. Empang, no ORCID, 3 works, 1 citation. Last known and affiliated: Caraga State University (2024, 2026). Initial-dropped search did not run. |
| 44 | Klinth Jerald L. Matugas | unambiguous | A5159600799 | One roster-search hit. A5159600799, Klinth Jerald L. Matugas, no ORCID, 2 works, 0 citations. Last known and affiliated: Caraga State University (2026). Initial-dropped search did not run. |
| 45 | Al Christian Plaza | unambiguous | A5159651905 | One hit. A5159651905, Al Christian Plaza, no ORCID, 1 work, 0 citations. Last known and affiliated: Caraga State University (2026). |
| 46 | Jessie Lynde M. Poralan | miss | none | `search=Jessie Lynde M. Poralan` returned count 0. Initial-dropped search did not run. |
| 47 | Junward B. Megullas | miss | none | `search=Junward B. Megullas` returned count 0. Initial-dropped search did not run. |
| 48 | Mary Abigail D. Soliva | unambiguous | A5159645669 | One roster-search hit. A5159645669, Mary Abigail D. Soliva, no ORCID, 2 works, 0 citations. Last known and affiliated: Caraga State University (2026). Initial-dropped search did not run. |
| 49 | Fritzie T. Nuez | miss | none | `search=Fritzie T. Nuez` returned count 0. Initial-dropped search did not run. |

## Split

- **John Mark B. Correa.** Exact roster name is the Caraga State University record `A5120889243` (1 work). `A5120346959` is "John Mark Correa" at Pangasinan State University (2 works, 2025) and appears only when the middle initial is removed. Same given names and surname, different institution, initial absent rather than contradictory.
- **Riah E. Encarnacion.** Three Caraga State University profiles. The 28-work record's display name expands E. to Elcullada. Its last known institution on this fetch is Caraga State University; University of Nizwa is a 2021 affiliation, and Surigao del Norte State University is a 2024 affiliation. The 1-work record's display name adds "Dit".
- **Clark Justine L. Gonzales.** Two Caraga State University profiles: `A5121242116` (with L., 2 works, 2025) and `A5159636087` (without L., 1 work, 2026).
- **Jaymer M. Jayoma.** `A5067578352` is the Caraga State University profile (34 works, ORCID https://orcid.org/0000-0001-7063-2693). `A5065766137` is "Jaymer Mernilo Jayoma" (1 work, 2011) with no institution. The middle initial may be Mernilo.
- **Junrie B. Matias.** `A5075735598` (37 works, ORCID https://orcid.org/0000-0001-9638-4667, Caraga State University) is the only roster-string hit. `A5136129512` ("Junrie Matias", 3 works, 2 citations, Caraga State University, 2026, no ORCID) is still a separate author and is returned by `search=Junrie Matias`.

## Collision

- **James V. Presbitero.** The only roster-string hit is `A5049211925`. Display name matches. The only affiliation is De La Salle University in 2018, on the work "Assessing compliance of Philippine state universities to the data privacy act of 2012". Nothing on the author or that authorship names Caraga State University. A search for "James Presbitero" did not run.

## Miss

- **Mary Pilar J. Barber.** Count 0 for the roster string and for "Mary Pilar Barber".
- **Robert Lee M. Bawiga.** Count 0 for the roster string and for "Robert Lee Bawiga".
- **Cherry I. Tabada.** Count 0 for the roster string. "Cherry Tabada" was not requested on this run.
- **Jessie Lynde M. Poralan.** Count 0 for the roster string. "Jessie Lynde Poralan" was not requested.
- **Junward B. Megullas.** Count 0 for the roster string. "Junward Megullas" was not requested.
- **Fritzie T. Nuez.** Count 0 for the roster string. "Fritzie Nuez" was not requested.

## Other hits that are not second profiles

- `A5154439464` is returned for both Cristopher C. Abalorio and Gleen A. Dalaorao. Display name is the four-author string. One 2022 work. Raw affiliation strings on that authorship are empty. It is a byline stored as an author, not a second record of either person.
- `A5121147432`, Paolo S. Pacaldo, Caraga State University, 1 work (2025), is a different middle initial from Paolo L. Pacaldo. Listed under Paolo L. Pacaldo in the table so the ID is not dropped on the floor. Not counted as a split.

## Prior sample, re-checked on this run

- Klinth Jerald L. Matugas. `A5159600799`, Caraga State University, 2 works. Confirmed. ORCID is null. Citations are 0. Affiliation year on the record is 2026.
- Cherry Tabada. The roster string `Cherry I. Tabada` returned count 0. The shorter sample query was not re-requested after the budget error.
- Luisito I. Tabada. `A5029531959`, Caraga State University, 2 works. Confirmed. Citations are 1. Affiliation years are 2009 and 2014. ORCID is null.
- Junrie B. Matias. `A5075735598` still has ORCID https://orcid.org/0000-0001-9638-4667 and 37 works at Caraga State University. `A5136129512` still exists, display name Junrie Matias, 3 works, Caraga State University. The roster-string search does not return the second ID.
- Vicente A. Pitogo. `A5056076342`, display name Vicente Aquino Pitogo, ORCID https://orcid.org/0000-0002-2061-7521, Caraga State University. Confirmed. Works count on this fetch is 36. Citations are 99.
- Roland P. Abao. `A5047149755` is still the only hit. Last known institution is now Caraga State University, not Ateneo de Manila University. Ateneo remains an affiliation for 2021–2023. The sample's "top hit at Ateneo" description is stale. ORCID https://orcid.org/0000-0001-6281-3822, 17 works, 59 citations.
- Cristopher C. Abalorio. `A5010125303` is Caraga State University, 23 works, 46 citations, no ORCID. `A5154439464` is still the concatenated byline, 1 work.
- Riah E. Encarnacion. The three sample IDs still exist, with 28, 5, and 1 works. `A5011650373` last known institution is Caraga State University on this fetch. University of Nizwa is a 2021 affiliation, not the last known institution. The sample's "University of Nizwa (28 works)" line is stale as a last-known institution.
