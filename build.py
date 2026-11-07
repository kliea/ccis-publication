#!/usr/bin/env python3
"""Refresh the OpenAlex snapshot used by the React catalog.

Running this file asks OpenAlex and replaces public/snapshot.json.
The catalog UI is the React app. Opening it does not ask OpenAlex.
"""

import json
import re
import time
import unicodedata
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SITE = ROOT / "site"
SNAPSHOT = ROOT / "public" / "snapshot.json"
MAILTO = "mailto:research-publication@example.com"
API = "https://api.openalex.org/works"

# Bound OpenAlex author records. Unmatched researchers and the records the
# binding rule refuses are absent: Pangasinan John Mark Correa (A5120346959)
# and De La Salle James V. Presbitero (A5049211925).
BOUND_IDS = {
    "A5010125303",  # Cristopher C. Abalorio
    "A5047149755",  # Roland P. Abao
    "A5069971657",  # Jayrhom R. Almonteros
    "A5119335978",  # Glaicel A. Araneta
    "A5120905689",  # Jenelyn R. Asis
    "A5114984484",  # Nathan Kit A. Berro
    "A5083660397",  # Ronnel O. Cacho
    "A5084287731",  # Rudolph Joshua U. Candare
    "A5017749693",  # Hannah Faye A. Capoy
    "A5120889243",  # John Mark B. Correa, Caraga State University
    "A5058737285",  # James Earl D. Cubillas
    "A5120398403",  # John Michael F. Cutamora
    "A5079210661",  # Gleen A. Dalaorao
    "A5121232067",  # Jayson C. Dollete
    "A5116295811",  # Paulo A. Duga
    "A5011650373",  # Riah E. Encarnacion
    "A5120888696",  # Riah E. Encarnacion
    "A5159661622",  # Riah E. Encarnacion
    "A5092891555",  # John Binze B. Escol
    "A5121194004",  # Giovanni T. Esma
    "A5094089741",  # Kent T. Espejon
    "A5121242116",  # Clark Justine L. Gonzales
    "A5159636087",  # Clark Justine L. Gonzales
    "A5136212287",  # Edwin Manuel M. Jarlata
    "A5067578352",  # Jaymer M. Jayoma
    "A5065766137",  # Jaymer Mernilo Jayoma
    "A5075735598",  # Junrie B. Matias
    "A5136129512",  # Junrie Matias, Caraga State University
    "A5159661252",  # Angel Lorraine M. Morales
    "A5080108496",  # Edsel Matt O. Morales
    "A5070606721",  # Elbert S. Moyon
    "A5051861067",  # Takeyasu V. Nakazato
    "A5094188681",  # Maria Besa Joy M. Ortuyo
    "A5120349545",  # Paolo L. Pacaldo
    "A5024726538",  # Mark Phil B. Pacot
    "A5120349505",  # Kimberly Ann B. Palaran
    "A5094052604",  # Joanna Victoria S. Pitao
    "A5056076342",  # Vicente A. Pitogo
    "A5120926324",  # Mary Rose O. Raz
    "A5095934684",  # Dexter A. Romaguera
    "A5138715107",  # Jordylene G. Sagusay
    "A5023348383",  # Jesterlyn Q. Timosan
    "A5029531959",  # Luisito I. Tabada
    "A5120631089",  # Kier Patrick A. Empang
    "A5159600799",  # Klinth Jerald L. Matugas
    "A5159651905",  # Al Christian Plaza
    "A5159645669",  # Mary Abigail D. Soliva
}

# Searched once, on the next refresh, without the middle initial.
UNCHECKED = [
    ("Cherry I. Tabada", "Cherry Tabada"),
    ("Jessie Lynde M. Poralan", "Jessie Lynde Poralan"),
    ("Junward B. Megullas", "Junward Megullas"),
    ("Fritzie T. Nunez", "Fritzie Nunez"),
    ("Clarielyn Y. Grado", "Clarielyn Grado"),
]
MARKER = SITE / "unchecked-search.json"

ROSTER = [
    "Cristopher C. Abalorio",
    "Roland P. Abao",
    "Jayrhom R. Almonteros",
    "Glaicel A. Araneta",
    "Jenelyn R. Asis",
    "Mary Pilar J. Barber",
    "Robert Lee M. Bawiga",
    "Nathan Kit A. Berro",
    "Ronnel O. Cacho",
    "Rudolph Joshua U. Candare",
    "Hannah Faye A. Capoy",
    "John Mark B. Correa",
    "James Earl D. Cubillas",
    "John Michael F. Cutamora",
    "Gleen A. Dalaorao",
    "Jayson C. Dollete",
    "Paulo A. Duga",
    "Riah E. Encarnacion",
    "John Binze B. Escol",
    "Giovanni T. Esma",
    "Kent T. Espejon",
    "Clark Justine L. Gonzales",
    "Edwin Manuel M. Jarlata",
    "Jaymer M. Jayoma",
    "Junrie B. Matias",
    "Angel Lorraine M. Morales",
    "Edsel Matt O. Morales",
    "Elbert S. Moyon",
    "Takeyasu V. Nakazato",
    "Maria Besa Joy M. Ortuyo",
    "Paolo L. Pacaldo",
    "Mark Phil B. Pacot",
    "Kimberly Ann B. Palaran",
    "Joanna Victoria S. Pitao",
    "Vicente A. Pitogo",
    "James V. Presbitero",
    "Mary Rose O. Raz",
    "Dexter A. Romaguera",
    "Jordylene G. Sagusay",
    "Cherry I. Tabada",
    "Jesterlyn Q. Timosan",
    "Luisito I. Tabada",
    "Kier Patrick A. Empang",
    "Klinth Jerald L. Matugas",
    "Al Christian Plaza",
    "Jessie Lynde M. Poralan",
    "Junward B. Megullas",
    "Mary Abigail D. Soliva",
    "Fritzie T. Nunez",
    "Clarielyn Y. Grado",
]

# Rank is the faculty profile on page 3. The seven names absent from that
# profile are Lecturers. Clarielyn Y. Grado is a Lecturer.
# Department is Computer Science, Information Technology, or Information Systems.
# Each year requires at least ARTICLE_EACH_YEAR published articles.
FACULTY = (
    ("Cristopher C. Abalorio", "Asst. Prof I", "Computer Science"),
    ("Roland P. Abao", "Asst. Prof III", "Information Technology"),
    ("Jayrhom R. Almonteros", "Instructor I", "Information Systems"),
    ("Glaicel A. Araneta", "Instructor I", "Information Technology"),
    ("Jenelyn R. Asis", "Instructor I", "Information Technology"),
    ("Mary Pilar J. Barber", "Instructor I", "Information Systems"),
    ("Robert Lee M. Bawiga", "Instructor I", "Information Technology"),
    ("Nathan Kit A. Berro", "Asst. Prof I", "Information Technology"),
    ("Ronnel O. Cacho", "Instructor I", "Computer Science"),
    ("Rudolph Joshua U. Candare", "Asso. Prof IV", "Computer Science"),
    ("Hannah Faye A. Capoy", "Instructor I", "Information Systems"),
    ("John Mark B. Correa", "Instructor I", "Computer Science"),
    ("James Earl D. Cubillas", "Instructor I", "Computer Science"),
    ("John Michael F. Cutamora", "Instructor I", "Computer Science"),
    ("Gleen A. Dalaorao", "Professor V", "Information Technology"),
    ("Jayson C. Dollete", "Instructor I", "Information Systems"),
    ("Paulo A. Duga", "Instructor I", "Information Systems"),
    ("Riah E. Encarnacion", "Asst. Prof I", "Information Technology"),
    ("John Binze B. Escol", "Instructor I", "Computer Science"),
    ("Giovanni T. Esma", "Instructor I", "Information Technology"),
    ("Kent T. Espejon", "Instructor I", "Information Technology"),
    ("Clark Justine L. Gonzales", "Instructor I", "Computer Science"),
    ("Edwin Manuel M. Jarlata", "Instructor I", "Information Technology"),
    ("Jaymer M. Jayoma", "Professor VI", "Computer Science"),
    ("Junrie B. Matias", "Professor VI", "Computer Science"),
    ("Angel Lorraine M. Morales", "Instructor I", "Computer Science"),
    ("Edsel Matt O. Morales", "Instructor I", "Information Technology"),
    ("Elbert S. Moyon", "Asst. Prof I", "Information Systems"),
    ("Takeyasu V. Nakazato", "Asso. Prof III", "Computer Science"),
    ("Maria Besa Joy M. Ortuyo", "Asso. Prof V", "Computer Science"),
    ("Paolo L. Pacaldo", "Instructor I", "Information Technology"),
    ("Mark Phil B. Pacot", "Asso. Prof V", "Computer Science"),
    ("Kimberly Ann B. Palaran", "Instructor I", "Information Systems"),
    ("Joanna Victoria S. Pitao", "Instructor I", "Computer Science"),
    ("Vicente A. Pitogo", "Professor VI", "Information Systems"),
    ("James V. Presbitero", "Asso. Prof I", "Information Technology"),
    ("Mary Rose O. Raz", "Instructor I", "Information Technology"),
    ("Dexter A. Romaguera", "Instructor I", "Information Technology"),
    ("Jordylene G. Sagusay", "Instructor I", "Information Systems"),
    ("Cherry I. Tabada", "Asst. Prof III", "Information Technology"),
    ("Jesterlyn Q. Timosan", "Asso. Prof V", "Information Systems"),
    ("Luisito I. Tabada", "Professor V", "Computer Science"),
    ("Kier Patrick A. Empang", "Lecturer", "Information Technology"),
    ("Klinth Jerald L. Matugas", "Lecturer", "Computer Science"),
    ("Al Christian Plaza", "Lecturer", "Information Systems"),
    ("Jessie Lynde M. Poralan", "Lecturer", "Information Systems"),
    ("Junward B. Megullas", "Lecturer", "Computer Science"),
    ("Mary Abigail D. Soliva", "Lecturer", "Information Systems"),
    ("Fritzie T. Nunez", "Lecturer", "Information Technology"),
    ("Clarielyn Y. Grado", "Lecturer", "Computer Science"),
)


def tokens(name):
    folded = unicodedata.normalize("NFD", name or "")
    folded = "".join(ch for ch in folded if unicodedata.category(ch) != "Mn")
    cleaned = re.sub(r"[^A-Za-z\s]", " ", folded)
    return [part for part in cleaned.split() if part]


def author_fits_roster(author_name, roster_name):
    """True when the byline name is that researcher.

    The first name and surname must match. A middle name on the byline must
    agree with the roster. A middle initial the byline leaves out still matches.
    """
    author = tokens(author_name)
    roster = tokens(roster_name)
    if len(author) < 2 or len(roster) < 2:
        return False
    if author[0].lower() != roster[0].lower():
        return False
    if author[-1].lower() != roster[-1].lower():
        return False
    roster_middles = roster[1:-1]
    for part in author[1:-1]:
        letter = part[0].lower()
        if not any(
            part.lower() == middle.lower() or letter == middle[0].lower()
            for middle in roster_middles
        ):
            return False
    return True


def is_roster_name(author_name):
    return any(author_fits_roster(author_name, roster_name) for roster_name in ROSTER)


def openalex_id(value):
    if not value:
        return ""
    return str(value).rstrip("/").rsplit("/", 1)[-1]


def get_json(url):
    if "mailto=" not in url:
        url += ("&" if "?" in url else "?") + "mailto=research-publication@example.com"
    delay = 5
    for attempt in range(6):
        request = urllib.request.Request(url, headers={"User-Agent": MAILTO})
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                return json.load(response)
        except urllib.error.HTTPError as error:
            if error.code not in (401, 429, 500, 503) or attempt == 5:
                raise
            time.sleep(delay)
            delay *= 2


def institutions(author):
    names = []
    for institution in author.get("last_known_institutions") or []:
        name = (institution or {}).get("display_name") or ""
        if name:
            names.append(name)
    return names


def search_unchecked():
    """One pass, without the middle initial. Later refreshes leave the marker alone."""
    if MARKER.exists():
        saved = json.loads(MARKER.read_text())
        return set(saved.get("bound_ids") or [])
    found = {}
    for roster_name, query in UNCHECKED:
        url = "https://api.openalex.org/authors?" + urllib.parse.urlencode({"search": query})
        payload = get_json(url)
        hits = []
        for author in payload.get("results") or []:
            display = author.get("display_name") or ""
            if author_fits_roster(display, roster_name):
                hits.append(author)
        if len(hits) == 1:
            chosen = [openalex_id(hits[0].get("id"))]
        else:
            chosen = []
            for author in hits:
                places = institutions(author)
                at_caraga = any("Caraga State University" in place for place in places)
                if at_caraga or not places:
                    chosen.append(openalex_id(author.get("id")))
        found[roster_name] = [author_id for author_id in chosen if author_id]
        time.sleep(0.2)
    bound_ids = sorted({author_id for ids in found.values() for author_id in ids})
    MARKER.write_text(json.dumps({"bound_ids": bound_ids, "found": found}, indent=2) + "\n")
    return set(bound_ids)


YEARS = (2023, 2024, 2025, 2026)
YEAR_TARGET = 36
ARTICLE_EACH_YEAR = 2


def fetch_works(author_ids):
    works = []
    seen = set()
    for author_id in sorted(author_ids):
        page = 1
        while True:
            query = urllib.parse.urlencode(
                {
                    "filter": f"authorships.author.id:{author_id},publication_year:{YEARS[0]}-{YEARS[-1]}",
                    "per_page": "200",
                    "page": str(page),
                }
            )
            payload = get_json(f"{API}?{query}")
            for work in payload.get("results") or []:
                work_id = work.get("id")
                if work_id in seen:
                    continue
                seen.add(work_id)
                works.append(work)
            count = (payload.get("meta") or {}).get("count") or 0
            if page * 200 >= count:
                break
            page += 1
            time.sleep(0.2)
        time.sleep(0.15)
    return works


def money(amount):
    if not isinstance(amount, dict) or amount.get("value") is None:
        return ""
    value = amount["value"]
    if isinstance(value, float) and value.is_integer():
        value = int(value)
    currency = amount.get("currency") or ""
    return f"{value} {currency}".strip()


def charge(work):
    paid = money(work.get("apc_paid"))
    if paid:
        return paid
    return money(work.get("apc_list"))


def source_of(work):
    location = work.get("primary_location") or {}
    return location.get("source") or {}


def issn_of(work):
    source = source_of(work)
    if source.get("issn_l"):
        return source["issn_l"]
    issns = source.get("issn") or []
    return issns[0] if issns else ""


def sponsors_of(work):
    names = []
    for funder in work.get("funders") or []:
        name = (funder or {}).get("display_name")
        if name and name not in names:
            names.append(name)
    publisher = source_of(work).get("host_organization_name") or ""
    if publisher and names:
        return publisher + "; " + "; ".join(names)
    return publisher or "; ".join(names)


def authors_of(work):
    authors = []
    for authorship in work.get("authorships") or []:
        name = authorship.get("raw_author_name") or ""
        author = authorship.get("author") or {}
        if not name:
            name = author.get("display_name") or ""
        if not name:
            continue
        author_id = openalex_id(author.get("id"))
        roster = author_id in BOUND_IDS or is_roster_name(name)
        authors.append({"name": name, "roster": roster})
    return authors


def link_of(work):
    doi = work.get("doi") or ""
    return doi if isinstance(doi, str) else ""


def date_of(work):
    return work.get("publication_date") or str(work.get("publication_year") or "")


def venue_of(work):
    return source_of(work).get("display_name") or ""


def title_of(work):
    return work.get("title") or work.get("display_name") or ""


SDGS = [
    (1, "No poverty"),
    (2, "Zero hunger"),
    (3, "Good health and well-being"),
    (4, "Quality education"),
    (5, "Gender equality"),
    (6, "Clean water and sanitation"),
    (7, "Affordable and clean energy"),
    (8, "Decent work and economic growth"),
    (9, "Industry, innovation and infrastructure"),
    (10, "Reduced inequalities"),
    (11, "Sustainable cities and communities"),
    (12, "Responsible consumption and production"),
    (13, "Climate action"),
    (14, "Life below water"),
    (15, "Life on land"),
    (16, "Peace, justice, and strong institutions"),
    (17, "Partnerships for the goals"),
]
SDG_NAMES = dict(SDGS)


def sdgs_of(work):
    found = []
    seen = set()
    for goal in work.get("sustainable_development_goals") or []:
        number = int(openalex_id(goal.get("id")) or 0)
        if number not in SDG_NAMES or number in seen:
            continue
        seen.add(number)
        found.append({"number": number, "name": SDG_NAMES[number]})
    found.sort(key=lambda goal: goal["number"])
    return found


def row_from(work):
    return {
        "id": openalex_id(work.get("id")),
        "title": title_of(work),
        "authors": authors_of(work),
        "venue": venue_of(work),
        "sponsor": sponsors_of(work),
        "issn": issn_of(work),
        "date": date_of(work),
        "year": int(work.get("publication_year") or 0),
        "charge": charge(work),
        "doi": link_of(work),
        "sdgs": sdgs_of(work),
        "indexes": [],
    }


def same_work_key(row):
    if row["doi"]:
        return "doi:" + row["doi"].rstrip("/").lower()
    return "id:" + row["id"]


def collapse(rows):
    chosen = {}
    for row in rows:
        key = same_work_key(row)
        current = chosen.get(key)
        if current is None or len(row["authors"]) > len(current["authors"]):
            chosen[key] = row
    return list(chosen.values())


def sort_key(row):
    title = row["title"].casefold()
    link = row["doi"].casefold()
    missing_link = 0 if link else 1
    date = row["date"] or "9999-99-99"
    return (title, missing_link, link, date)


def build_rows(works):
    rows = collapse(row_from(work) for work in works)
    rows = [row for row in rows if YEARS[0] <= row["year"] <= YEARS[-1]]
    rows.sort(key=sort_key)
    return rows


def carry_indexes(rows):
    path = SNAPSHOT if SNAPSHOT.exists() else SITE / "snapshot.json"
    if not path.exists():
        return rows
    previous = json.loads(path.read_text()).get("rows") or []
    saved = {row.get("id"): row.get("indexes") or [] for row in previous}
    for row in rows:
        if not row.get("indexes"):
            row["indexes"] = list(saved.get(row.get("id")) or [])
    return rows


def main():
    works = fetch_works(BOUND_IDS | search_unchecked())
    rows = carry_indexes(build_rows(works))
    built_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    payload = {
        "built_at": built_at,
        "publication_year": f"{YEARS[0]}-{YEARS[-1]}",
        "count": len(rows),
        "rows": rows,
    }
    text = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    SNAPSHOT.parent.mkdir(exist_ok=True)
    SNAPSHOT.write_text(text)
    SITE.mkdir(exist_ok=True)
    (SITE / "snapshot.json").write_text(text)
    print(f"wrote {len(rows)} publications to {SNAPSHOT}")


if __name__ == "__main__":
    main()
