#!/usr/bin/env python3
"""Build the static publication catalog from the saved OpenAlex snapshot.

Running this file is a refresh: it asks OpenAlex, replaces site/snapshot.json,
and prepares site/index.html again. Opening the site does not ask OpenAlex.
"""

import html
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
]

# Rank is the faculty profile on page 3. The seven names absent from that
# profile are Lecturers. Unit is blank when the profile lists no department.
# Each year requires at least ARTICLE_EACH_YEAR published articles.
FACULTY = (
    ("Cristopher C. Abalorio", "Asst. Prof I", ""),
    ("Roland P. Abao", "Asst. Prof III", "Information Technology"),
    ("Jayrhom R. Almonteros", "Instructor I", "Information Systems"),
    ("Glaicel A. Araneta", "Instructor I", ""),
    ("Jenelyn R. Asis", "Instructor I", "Information Technology"),
    ("Mary Pilar J. Barber", "Instructor I", ""),
    ("Robert Lee M. Bawiga", "Instructor I", ""),
    ("Nathan Kit A. Berro", "Asst. Prof I", ""),
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
    ("John Binze B. Escol", "Instructor I", ""),
    ("Giovanni T. Esma", "Instructor I", "Information Technology"),
    ("Kent T. Espejon", "Instructor I", ""),
    ("Clark Justine L. Gonzales", "Instructor I", "Computer Science"),
    ("Edwin Manuel M. Jarlata", "Instructor I", "Information Technology"),
    ("Jaymer M. Jayoma", "Professor VI", "Computer Science"),
    ("Junrie B. Matias", "Professor VI", "Computer Science"),
    ("Angel Lorraine M. Morales", "Instructor I", ""),
    ("Edsel Matt O. Morales", "Instructor I", "Information Technology"),
    ("Elbert S. Moyon", "Asst. Prof I", "Information Systems"),
    ("Takeyasu V. Nakazato", "Asso. Prof III", "Computer Science"),
    ("Maria Besa Joy M. Ortuyo", "Asso. Prof V", "Computer Science"),
    ("Paolo L. Pacaldo", "Instructor I", ""),
    ("Mark Phil B. Pacot", "Asso. Prof V", "Computer Science"),
    ("Kimberly Ann B. Palaran", "Instructor I", "Information Systems"),
    ("Joanna Victoria S. Pitao", "Instructor I", "Computer Science"),
    ("Vicente A. Pitogo", "Professor VI", "Information Systems"),
    ("James V. Presbitero", "Asso. Prof I", "Information Technology"),
    ("Mary Rose O. Raz", "Instructor I", "Information Technology"),
    ("Dexter A. Romaguera", "Instructor I", "Information Technology"),
    ("Jordylene G. Sagusay", "Instructor I", ""),
    ("Cherry I. Tabada", "Asst. Prof III", "Information Technology"),
    ("Jesterlyn Q. Timosan", "Asso. Prof V", "Information Systems"),
    ("Luisito I. Tabada", "Professor V", "Computer Science"),
    ("Kier Patrick A. Empang", "Lecturer", ""),
    ("Klinth Jerald L. Matugas", "Lecturer", ""),
    ("Al Christian Plaza", "Lecturer", ""),
    ("Jessie Lynde M. Poralan", "Lecturer", ""),
    ("Junward B. Megullas", "Lecturer", ""),
    ("Mary Abigail D. Soliva", "Lecturer", ""),
    ("Fritzie T. Nunez", "Lecturer", ""),
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


def escape(value):
    return html.escape(value or "", quote=True)


def author_html(authors):
    parts = []
    for author in authors:
        name = escape(author["name"])
        if author["roster"]:
            parts.append(f'<strong class="roster">{name}</strong>')
        else:
            parts.append(name)
    return ", ".join(parts)


def cell(value):
    if not value:
        return '<span class="blank">—</span>'
    return escape(value)


INDEX_LABELS = (
    ("scopus", "Scopus"),
    ("wos", "Web of Science"),
    ("aci", "Asian Citation Index"),
)


def index_text(row):
    found = set(row.get("indexes") or [])
    return "; ".join(name for key, name in INDEX_LABELS if key in found)


def carry_indexes(rows):
    path = SITE / "snapshot.json"
    if not path.exists():
        return rows
    previous = json.loads(path.read_text()).get("rows") or []
    saved = {row.get("id"): row.get("indexes") or [] for row in previous}
    for row in rows:
        if not row.get("indexes"):
            row["indexes"] = list(saved.get(row.get("id")) or [])
    return rows


def link_cell(doi):
    if not doi:
        return '<span class="blank">—</span>'
    safe = escape(doi)
    return f'<a href="{safe}">{safe}</a>'


def year_options(rows):
    counts = {year: 0 for year in YEARS}
    for row in rows:
        if row["year"] in counts:
            counts[row["year"]] += 1
    options = ['<option value="">All</option>']
    for year in YEARS:
        options.append(f'<option value="{year}">{year} ({counts[year]})</option>')
    return "".join(options)


def sdg_options(rows):
    counts = {number: 0 for number, _name in SDGS}
    for row in rows:
        for goal in row.get("sdgs") or []:
            counts[goal["number"]] = counts.get(goal["number"], 0) + 1
    options = ['<option value="">All</option>']
    for number, name in SDGS:
        options.append(
            f'<option value="{number}">{number} {escape(name)} ({counts[number]})</option>'
        )
    return "".join(options)


def percent(part, whole):
    if not whole:
        return "0.0%"
    return f"{part / whole * 100:.1f}%"


def kpi_section(rows):
    published = {year: 0 for year in YEARS}
    indexes = {"scopus": 0, "wos": 0, "aci": 0}
    for row in rows:
        if row.get("year") in published:
            published[row["year"]] += 1
        for key in row.get("indexes") or []:
            if key in indexes:
                indexes[key] += 1
    body = []
    for year in YEARS:
        count = published[year]
        remaining = max(0, YEAR_TARGET - count)
        status = "Achieved" if count >= YEAR_TARGET else "Below Target"
        body.append(
            "<tr>"
            f"<td>{year}</td>"
            f'<td class="num">{count}</td>'
            f'<td class="num">{YEAR_TARGET}</td>'
            f'<td class="num">{percent(count, YEAR_TARGET)}</td>'
            f'<td class="num">{remaining}</td>'
            f"<td>{status}</td>"
            "</tr>"
        )
    labels = (
        ("scopus", "Scopus"),
        ("wos", "Web of Science (WoS)"),
        ("aci", "Asian Citation Index (ACI)"),
    )
    total = sum(indexes.values())
    index_rows = []
    for key, label in labels:
        index_rows.append(
            "<tr>"
            f"<td>{escape(label)}</td>"
            f'<td class="num">{indexes[key]}</td>'
            f'<td class="num">{percent(indexes[key], total)}</td>'
            "</tr>"
        )
    index_rows.append(
        '<tr class="total">'
        "<td>Total Indexed Articles</td>"
        f'<td class="num">{total}</td>'
        f'<td class="num">{percent(total, total)}</td>'
        "</tr>"
    )
    return f"""
    <h1>KPI</h1>
    <p class="legend">Annual target is {YEAR_TARGET} published works for each year. % Target Achieved is that year's published works divided by {YEAR_TARGET}.</p>
    <div class="scroll">
      <table class="summary">
        <thead>
          <tr>
            <th>Year</th>
            <th class="num">Total Articles</th>
            <th class="num">Annual Target</th>
            <th class="num">% Target Achieved</th>
            <th class="num">Remaining Target</th>
            <th>Performance Status</th>
          </tr>
        </thead>
        <tbody>{"".join(body)}</tbody>
      </table>
    </div>
    <h2>Indexing breakdown</h2>
    <p class="legend">% Share is the database count divided by the sum of the three counts. A work listed in two databases is counted in each.</p>
    <div class="scroll">
      <table class="summary">
        <thead>
          <tr>
            <th>Indexing Database</th>
            <th class="num">Total Count</th>
            <th class="num">% Share</th>
          </tr>
        </thead>
        <tbody>{"".join(index_rows)}</tbody>
      </table>
    </div>
    """


def faculty_year_counts(rows, name):
    counts = {year: 0 for year in YEARS}
    for row in rows:
        year = row.get("year")
        if year not in counts:
            continue
        if any(author_fits_roster(author["name"], name) for author in row["authors"]):
            counts[year] += 1
    return counts


def faculty_section(rows):
    if [item[0] for item in FACULTY] != ROSTER:
        raise SystemExit("Faculty names and roster names differ")
    body = []
    for number, (name, rank, unit) in enumerate(FACULTY, start=1):
        counts = faculty_year_counts(rows, name)
        year_cells = "".join(
            f'<td class="num" data-year="{year}">{counts[year]}</td>' for year in YEARS
        )
        body.append(
            "<tr>"
            f"<td>{number}</td>"
            f"<td>{escape(name)}</td>"
            f"<td>{escape(rank)}</td>"
            f"<td>{cell(unit)}</td>"
            f'<td class="num">{ARTICLE_EACH_YEAR}</td>'
            f"{year_cells}"
            "</tr>"
        )
    year_headers = "".join(
        f'<th class="num" data-year="{year}">{year}</th>' for year in YEARS
    )
    year_options = ['<option value="">All</option>']
    year_options.extend(f'<option value="{year}">{year}</option>' for year in YEARS)
    return f"""
    <h1>Faculty summary</h1>
    <p class="legend">{len(FACULTY)} faculty. Each year requires at least {ARTICLE_EACH_YEAR} published articles. The year columns are Article - Accepted/Published for that year.</p>
    <div class="filters">
      <label for="faculty-year">Year</label>
      <select id="faculty-year">{"".join(year_options)}</select>
    </div>
    <div class="scroll">
      <table class="summary" id="faculty-table">
        <thead>
          <tr>
            <th>No.</th>
            <th>Name</th>
            <th>Rank</th>
            <th>Unit</th>
            <th class="num">Req. Article</th>
            {year_headers}
          </tr>
        </thead>
        <tbody>{"".join(body)}</tbody>
      </table>
    </div>
    """


def page(rows, built_at):
    body_rows = []
    for index, row in enumerate(rows, start=1):
        body_rows.append(
            f'<tr data-open data-index="{index - 1}">'
            f"<td>{index}</td>"
            f"<td>{author_html(row['authors'])}</td>"
            f"<td>{cell(row['title'])}</td>"
            f"<td>{cell(row['venue'])}</td>"
            f"<td>{cell(row['sponsor'])}</td>"
            '<td><span class="blank">—</span></td>'
            f"<td>{cell(index_text(row))}</td>"
            '<td><span class="blank">—</span></td>'
            f"<td>{cell(row['issn'])}</td>"
            "<td>Published</td>"
            f"<td>{cell(row['date'])}</td>"
            f"<td>{cell(row['charge'])}</td>"
            f"<td>{link_cell(row['doi'])}</td>"
            "</tr>"
        )
    data = json.dumps(rows, ensure_ascii=False).replace("<", "\\u003c")
    count = len(rows)
    noun = "publication" if count == 1 else "publications"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Publication catalog</title>
  <link rel="icon" href="ccis-logo.png" type="image/png" />
  <link rel="apple-touch-icon" href="ccis-logo.png" />
  <meta property="og:title" content="Publication catalog" />
  <meta property="og:image" content="ccis-logo.png" />
  <meta property="og:image:type" content="image/png" />
  <meta property="og:image:width" content="600" />
  <meta property="og:image:height" content="600" />
  <meta property="og:image:alt" content="CSU CCIS, College of Computing and Information Sciences" />
  <meta name="twitter:card" content="summary" />
  <meta name="twitter:image" content="ccis-logo.png" />
  <meta name="twitter:image:alt" content="CSU CCIS, College of Computing and Information Sciences" />
  <style>
    :root {{
      color-scheme: light;
      --navy: #0b1c33;
      --dusk: #1f4b7a;
      --paper: #ffffff;
      --wash: #e7eef6;
      --line: #d0dced;
      --muted: #5d738c;
      --orange: #f08a2a;
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; font: 16px/1.45 "Iowan Old Style", Palatino, Georgia, serif; color: var(--navy); background: white; }}
    :focus-visible {{ outline: 2px solid var(--orange); outline-offset: 2px; }}
    .site-nav {{ position: sticky; top: 0; z-index: 5; display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 12px 24px; padding: 14px 20px; background: var(--dusk); font: 14px/1.3 ui-sans-serif, system-ui, sans-serif; }}
    .brand {{ display: flex; align-items: center; gap: 10px; color: white; font-weight: 650; letter-spacing: .01em; }}
    .brand img {{ width: 36px; height: 36px; border-radius: 50%; background: white; }}
    .views {{ display: flex; flex-wrap: wrap; gap: 6px; }}
    .site-nav button {{ font: inherit; color: white; background: transparent; border: 0; border-bottom: 3px solid transparent; padding: 8px 12px; cursor: pointer; }}
    .site-nav button:hover {{ color: var(--orange); }}
    .site-nav button[aria-current="page"] {{ color: white; border-bottom-color: var(--orange); }}
    section[hidden] {{ display: none; }}
    main {{ padding: 28px 16px 48px; max-width: 1440px; margin: 0 auto; }}
    h1 {{ font-size: 28px; font-weight: 600; margin: 0 0 4px; color: var(--dusk); }}
    h2 {{ font-size: 22px; font-weight: 600; margin: 28px 0 8px; color: var(--dusk); }}
    .summary th {{ padding: 8px 10px; }}
    .summary .num {{ text-align: right; font-variant-numeric: tabular-nums; }}
    .summary tr.total td {{ font-weight: 700; background: var(--wash); }}
    .sub {{ margin: 0 0 8px; color: var(--navy); }}
    .legend {{ margin: 0 0 12px; color: var(--navy); font-size: 14px; }}
    .filters {{ display: flex; flex-wrap: wrap; align-items: center; gap: 10px; margin: 0 0 16px; font: 14px/1.3 ui-sans-serif, system-ui, sans-serif; }}
    .filters label, .rows-label {{ color: var(--navy); }}
    .filters select, .table-foot select {{ font: inherit; color: var(--navy); background: white; border: 1px solid var(--dusk); border-radius: 8px; padding: 6px 8px; }}
    #year, #faculty-year {{ max-width: 140px; }}
    #sdg {{ max-width: min(100%, 320px); }}
    .filters button {{ font: inherit; color: var(--navy); background: var(--orange); border: 0; border-radius: 8px; padding: 8px 12px; font-weight: 650; cursor: pointer; }}
    .filters button:hover {{ background: #ff9d45; }}
    .table-foot {{ display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 12px 24px; margin: 12px 0 0; font: 14px/1.3 ui-sans-serif, system-ui, sans-serif; }}
    .table-foot[hidden] {{ display: none; }}
    .range {{ margin: 0; color: var(--navy); }}
    .table-foot-controls {{ display: flex; flex-wrap: wrap; align-items: center; gap: 16px; margin-left: auto; }}
    .table-foot select {{ height: 32px; }}
    .pager ul {{ display: flex; align-items: center; gap: 4px; list-style: none; margin: 0; padding: 0; }}
    .pager button {{ font: inherit; display: inline-flex; align-items: center; justify-content: center; gap: 4px; height: 36px; min-width: 36px; padding: 0 8px; color: var(--navy); background: transparent; border: 1px solid transparent; border-radius: 8px; cursor: pointer; }}
    .pager button:hover:not(:disabled) {{ background: var(--wash); }}
    .pager button[aria-current="page"] {{ color: var(--navy); background: var(--orange); border-color: var(--orange); }}
    .pager button.step {{ padding: 0 10px; }}
    .pager button:disabled {{ color: #8aa0b8; cursor: default; }}
    .pager svg {{ width: 16px; height: 16px; }}
    .pager .ellipsis {{ display: flex; width: 36px; height: 36px; align-items: center; justify-content: center; color: var(--navy); }}
    .sr-only {{ position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden; clip: rect(0, 0, 0, 0); white-space: nowrap; border: 0; }}
    @media (max-width: 640px) {{
      .site-nav {{ align-items: stretch; }}
      .views {{ width: 100%; }}
      .views button {{ flex: 1; }}
      .step-label {{ position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden; clip: rect(0, 0, 0, 0); white-space: nowrap; border: 0; }}
    }}
    .empty {{ display: none; margin: 0 0 12px; color: var(--navy); }}
    tr[hidden] {{ display: none; }}
    .scroll {{ overflow-x: auto; border: 1px solid var(--line); border-radius: 12px; background: white; color: var(--navy); }}
    table {{ width: 100%; border-collapse: collapse; font: 13px/1.35 ui-sans-serif, system-ui, sans-serif; }}
    caption {{ caption-side: bottom; padding: 8px 10px; text-align: left; color: var(--muted); }}
    th, td {{ border-bottom: 1px solid var(--line); padding: 8px 10px; vertical-align: top; text-align: left; }}
    th {{ background: var(--dusk); color: white; font-weight: 650; white-space: nowrap; position: sticky; top: 0; padding: 0; }}
    #faculty-table [hidden] {{ display: none; }}
    th button {{ font: inherit; font-weight: 650; display: flex; align-items: center; justify-content: space-between; gap: 8px; width: 100%; padding: 8px 10px; color: inherit; background: transparent; border: 0; cursor: pointer; text-align: left; white-space: nowrap; }}
    th button:hover {{ background: rgba(255, 255, 255, .08); }}
    .sort-icon {{ display: inline-flex; width: 14px; height: 14px; flex: none; }}
    .sort-icon svg {{ width: 14px; height: 14px; }}
    tr[data-open] {{ cursor: pointer; }}
    tr[data-open]:hover td {{ background: var(--wash); }}
    .blank {{ color: #8aa0b8; }}
    .roster {{ font-weight: 700; color: var(--navy); }}
    a {{ color: var(--dusk); }}
    a:hover {{ color: #9a3e08; }}
    .modal-back {{ position: fixed; inset: 0; background: rgba(11, 28, 51, .55); display: flex; align-items: flex-start; justify-content: center; padding: 48px 16px; }}
    .modal {{ background: white; color: var(--navy); border-radius: 12px; border-top: 4px solid var(--orange); max-width: 720px; width: 100%; padding: 22px; max-height: calc(100vh - 96px); overflow: auto; }}
    .modal h2 {{ margin: 0 40px 16px 0; font-size: 22px; line-height: 1.3; color: var(--dusk); }}
    .modal-close {{ float: right; font: 13px/1 ui-sans-serif, system-ui, sans-serif; color: var(--navy); background: white; border: 1px solid var(--dusk); border-radius: 8px; padding: 6px 10px; cursor: pointer; }}
    .ruled {{ border-bottom: 1px solid var(--line); padding: 8px 0; display: grid; grid-template-columns: 180px 1fr; gap: 12px; font: 14px/1.4 ui-sans-serif, system-ui, sans-serif; }}
    .ruled span {{ color: var(--muted); }}
    .kpi-head {{ margin: 18px 0 0; font: 600 13px/1.4 ui-sans-serif, system-ui, sans-serif; color: var(--muted); }}
    #kpi[hidden] {{ display: none; }}
  </style>
</head>
<body>
  <nav class="site-nav" aria-label="Catalog views">
    <div class="brand">
      <img src="ccis-logo.png" alt="" width="36" height="36" />
      <span>CCIS catalog</span>
    </div>
    <div class="views">
      <button type="button" data-view="kpi">KPI</button>
      <button type="button" data-view="publication" aria-current="page">Publication</button>
      <button type="button" data-view="faculty">Faculty summary</button>
    </div>
  </nav>
  <main>
    <section id="view-kpi" hidden>
      {kpi_section(rows)}
    </section>
    <section id="view-publication">
    <h1>Publication catalog</h1>
    <p class="sub" id="count">{count} {noun} · {YEARS[0]}–{YEARS[-1]} · snapshot {escape(built_at)}</p>
    <p class="legend">Bold names are researchers on the roster. Choose a row for the full record. A link opens the work and leaves the table in place.</p>
    <div class="filters">
      <label for="year">Year</label>
      <select id="year">{year_options(rows)}</select>
      <label for="sdg">SDG</label>
      <select id="sdg">{sdg_options(rows)}</select>
      <button type="button" id="export-excel">Export Excel</button>
      <button type="button" id="export-pdf">Export PDF</button>
    </div>
    <p class="empty" id="empty">No publications for that year and goal.</p>
    <div class="scroll">
      <table id="publications">
        <caption class="sub">Published works recorded for {YEARS[0]}–{YEARS[-1]}.</caption>
        <thead>
          <tr>
            <th data-sort="number" aria-sort="none"><button type="button">No.<span class="sort-icon" aria-hidden="true"></span></button></th>
            <th data-sort="authors" aria-sort="none"><button type="button">Author/s<span class="sort-icon" aria-hidden="true"></span></button></th>
            <th data-sort="title" aria-sort="none"><button type="button">Title<span class="sort-icon" aria-hidden="true"></span></button></th>
            <th data-sort="venue" aria-sort="none"><button type="button">Journal / Conference<span class="sort-icon" aria-hidden="true"></span></button></th>
            <th data-sort="sponsor" aria-sort="none"><button type="button">Sponsor / Publisher<span class="sort-icon" aria-hidden="true"></span></button></th>
            <th data-sort="database" aria-sort="none"><button type="button">Database<span class="sort-icon" aria-hidden="true"></span></button></th>
            <th data-sort="indexing" aria-sort="none"><button type="button">Indexing<span class="sort-icon" aria-hidden="true"></span></button></th>
            <th data-sort="ranking" aria-sort="none"><button type="button">Ranking / JIF<span class="sort-icon" aria-hidden="true"></span></button></th>
            <th data-sort="issn" aria-sort="none"><button type="button">ISSN / ISBN<span class="sort-icon" aria-hidden="true"></span></button></th>
            <th data-sort="status" aria-sort="none"><button type="button">Status<span class="sort-icon" aria-hidden="true"></span></button></th>
            <th data-sort="date" aria-sort="none"><button type="button">Date<span class="sort-icon" aria-hidden="true"></span></button></th>
            <th data-sort="charge" aria-sort="none"><button type="button">Publication Charge<span class="sort-icon" aria-hidden="true"></span></button></th>
            <th data-sort="doi" aria-sort="none"><button type="button">Link / DOI<span class="sort-icon" aria-hidden="true"></span></button></th>
          </tr>
        </thead>
        <tbody>
          {"".join(body_rows)}
        </tbody>
      </table>
    </div>
    <div class="table-foot" id="table-foot">
      <p class="range" id="page-status"></p>
      <div class="table-foot-controls">
        <label class="rows-label" for="page-size">Rows per page</label>
        <select id="page-size">
          <option value="5" selected>5</option>
          <option value="10">10</option>
          <option value="25">25</option>
          <option value="50">50</option>
        </select>
        <nav class="pager" id="pager" aria-label="pagination">
          <ul id="pager-list"></ul>
        </nav>
      </div>
    </div>
    </section>
    <section id="view-faculty" hidden>
      {faculty_section(rows)}
    </section>
  </main>
  <script id="rows" type="application/json">{data}</script>
  <script src="export.js"></script>
  <script>
    const rows = JSON.parse(document.getElementById("rows").textContent);
    const blank = (value) => value ? escapeHtml(value) : '<span class="blank">—</span>';
    function escapeHtml(value) {{
      return String(value).replace(/[&<>"']/g, (ch) => ({{
        "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
      }}[ch]));
    }}
    const indexNames = {{ scopus: "Scopus", wos: "Web of Science", aci: "Asian Citation Index" }};
    function indexText(row) {{
      return (row.indexes || []).map((id) => indexNames[id]).filter(Boolean).join("; ");
    }}
    function authors(list) {{
      return list.map((author) => {{
        const name = escapeHtml(author.name);
        return author.roster ? '<strong class="roster">' + name + '</strong>' : name;
      }}).join(", ");
    }}
    function detail(row, number) {{
      const doi = row.doi
        ? '<a href="' + escapeHtml(row.doi) + '">' + escapeHtml(row.doi) + '</a>'
        : '<span class="blank">—</span>';
      const lines = [
        ["No.", String(number)],
        ["Author/s", authors(row.authors)],
        ["Title", blank(row.title)],
        ["Journal / Conference", blank(row.venue)],
        ["Sponsor / Publisher", blank(row.sponsor)],
        ["Database", blank("")],
        ["Indexing", indexText(row) ? escapeHtml(indexText(row)) : blank("")],
        ["Ranking / JIF", blank("")],
        ["ISSN / ISBN", blank(row.issn)],
        ["Status", "Published"],
        ["Date", blank(row.date)],
        ["Year", blank(String(row.year || ""))],
        ["Publication Charge", blank(row.charge)],
        ["Link / DOI", doi],
        ["SDG", (row.sdgs || []).length
          ? (row.sdgs || []).map((goal) => goal.number + " " + escapeHtml(goal.name)).join("; ")
          : '<span class="blank">—</span>']
      ];
      return lines.map(([label, value]) =>
        '<div class="ruled"><span>' + label + '</span><div>' + value + '</div></div>'
      ).join("");
    }}
    const YEAR_TARGET = 36;
    const INDEXES = [
      ["scopus", "Scopus"],
      ["wos", "Web of Science"],
      ["aci", "Asian Citation Index"]
    ];
    function openKpi(year) {{
      closeModal();
      const yearRows = rows.filter((row) => row.year === year);
      const counts = {{ scopus: 0, wos: 0, aci: 0 }};
      yearRows.forEach((row) => {{
        (row.indexes || []).forEach((id) => {{
          if (Object.prototype.hasOwnProperty.call(counts, id)) counts[id] += 1;
        }});
      }});
      const published = yearRows.length;
      const remaining = Math.max(0, YEAR_TARGET - published);
      const performance = (published / YEAR_TARGET * 100).toFixed(2) + "%";
      const lines = [
        ["Published", String(published)],
        ["Target", String(YEAR_TARGET)],
        ["Remaining Target", String(remaining)],
        ["Performance Status", performance]
      ];
      const indexLines = INDEXES.map(([id, name]) => [name, String(counts[id])]);
      const body = lines.concat(indexLines).map(([label, value], index) => {{
        const head = index === lines.length ? '<h3 class="kpi-head">Indexing</h3>' : "";
        return head + '<div class="ruled"><span>' + label + '</span><div>' + value + '</div></div>';
      }}).join("");
      const back = document.createElement("div");
      back.className = "modal-back";
      back.innerHTML = '<div class="modal" role="dialog" aria-modal="true" aria-labelledby="kpi-title">'
        + '<button type="button" class="modal-close">Close</button>'
        + '<h2 id="kpi-title">' + year + ' KPI</h2>'
        + body
        + '</div>';
      document.body.appendChild(back);
      const close = back.querySelector(".modal-close");
      close.addEventListener("click", closeModal);
      close.focus();
      back.addEventListener("click", (event) => {{
        if (event.target === back) closeModal();
      }});
    }}
    function closeModal() {{
      const back = document.querySelector(".modal-back");
      if (back) back.remove();
    }}
    function openModal(index) {{
      closeModal();
      const row = rows[index];
      const back = document.createElement("div");
      back.className = "modal-back";
      back.innerHTML = '<div class="modal" role="dialog" aria-modal="true" aria-labelledby="detail-title">'
        + '<button type="button" class="modal-close">Close</button>'
        + '<h2 id="detail-title">' + escapeHtml(row.title) + '</h2>'
        + detail(row, index + 1)
        + '</div>';
      document.body.appendChild(back);
      const close = back.querySelector(".modal-close");
      close.addEventListener("click", closeModal);
      close.focus();
      back.addEventListener("click", (event) => {{
        if (event.target === back) closeModal();
      }});
    }}
    const total = rows.length;
    const countEl = document.getElementById("count");
    const emptyEl = document.getElementById("empty");
    const footEl = document.getElementById("table-foot");
    const pagerEl = document.getElementById("pager");
    const pagerListEl = document.getElementById("pager-list");
    const pageStatusEl = document.getElementById("page-status");
    const sdgNames = {json.dumps(SDGS)};
    const arrowUp = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m5 12 7-7 7 7"/><path d="M12 19V5"/></svg>';
    const arrowDown = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 5v14"/><path d="m19 12-7 7-7-7"/></svg>';
    const chevronLeft = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m15 18-6-6 6-6"/></svg>';
    const chevronRight = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m9 18 6-6-6-6"/></svg>';
    const ellipsisIcon = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="1"/><circle cx="19" cy="12" r="1"/><circle cx="5" cy="12" r="1"/></svg>';
    let page = 1;
    let sortKey = null;
    let sortDir = "asc";
    function rowRecord(index) {{
      return Object.assign({{ number: index + 1 }}, rows[index]);
    }}
    function sortValue(row, key) {{
      if (key === "number") return row.number;
      if (key === "authors") return (row.authors || []).map((author) => author.name).join(", ");
      if (key === "title") return row.title || "";
      if (key === "venue") return row.venue || "";
      if (key === "sponsor") return row.sponsor || "";
      if (key === "issn") return row.issn || "";
      if (key === "indexing") return indexText(row);
      if (key === "status") return "Published";
      if (key === "date") return row.date || "";
      if (key === "charge") return row.charge || "";
      if (key === "doi") return row.doi || "";
      return "";
    }}
    function compareRows(a, b, key, dir) {{
      const av = sortValue(a, key);
      const bv = sortValue(b, key);
      const aBlank = av === "" || av == null;
      const bBlank = bv === "" || bv == null;
      if (aBlank && bBlank) return a.number - b.number;
      if (aBlank) return 1;
      if (bBlank) return -1;
      let result = 0;
      if (key === "number") result = av - bv;
      else if (key === "charge") {{
        const an = parseFloat(String(av).replace(/,/g, ""));
        const bn = parseFloat(String(bv).replace(/,/g, ""));
        result = !Number.isNaN(an) && !Number.isNaN(bn)
          ? an - bn
          : String(av).localeCompare(String(bv), undefined, {{ numeric: true, sensitivity: "base" }});
      }} else {{
        result = String(av).localeCompare(String(bv), undefined, {{ numeric: true, sensitivity: "base" }});
      }}
      if (result === 0) return a.number - b.number;
      return dir === "desc" ? -result : result;
    }}
    function paintSort() {{
      document.querySelectorAll("th[data-sort]").forEach((th) => {{
        const active = th.dataset.sort === sortKey;
        th.setAttribute("aria-sort", active ? (sortDir === "asc" ? "ascending" : "descending") : "none");
        th.querySelector(".sort-icon").innerHTML = active ? (sortDir === "asc" ? arrowUp : arrowDown) : "";
      }});
    }}
    window.catalogSortRows = function (list) {{
      if (!sortKey) return list;
      return list.slice().sort((a, b) => compareRows(a, b, sortKey, sortDir));
    }};
    function selectedYear() {{
      const value = document.getElementById("year").value;
      return value ? Number(value) : null;
    }}
    function pageSize() {{
      return Number(document.getElementById("page-size").value);
    }}
    function pageItems(current, total) {{
      if (total <= 7) return Array.from({{ length: total }}, (_, index) => index + 1);
      if (current <= 3) return [1, 2, 3, 4, "ellipsis", total];
      if (current >= total - 2) return [1, "ellipsis", total - 3, total - 2, total - 1, total];
      return [1, "ellipsis", current - 1, current, current + 1, "ellipsis", total];
    }}
    function renderPager(pages) {{
      const focused = document.activeElement;
      const focusStep = focused && focused.dataset ? focused.dataset.step : "";
      const focusPage = focused && focused.dataset && focused.dataset.page;
      const items = [
        '<li><button type="button" class="step" data-step="prev"' + (page <= 1 ? " disabled" : "") + ' aria-label="Go to previous page">' + chevronLeft + '<span class="step-label">Previous</span></button></li>'
      ];
      pageItems(page, pages).forEach((item) => {{
        if (item === "ellipsis") {{
          items.push('<li><span class="ellipsis">' + ellipsisIcon + '<span class="sr-only">More pages</span></span></li>');
          return;
        }}
        const current = item === page ? ' aria-current="page"' : "";
        items.push('<li><button type="button" data-page="' + item + '"' + current + ' aria-label="Page ' + item + '">' + item + "</button></li>");
      }});
      items.push('<li><button type="button" class="step" data-step="next"' + (page >= pages ? " disabled" : "") + ' aria-label="Go to next page"><span class="step-label">Next</span>' + chevronRight + "</button></li>");
      pagerListEl.innerHTML = items.join("");
      if (focusStep) {{
        const next = pagerListEl.querySelector('[data-step="' + focusStep + '"]');
        if (next && !next.disabled) next.focus();
      }} else if (focusPage) {{
        const next = pagerListEl.querySelector('[aria-current="page"]');
        if (next) next.focus();
      }}
    }}
    function applyFilters() {{
      const year = selectedYear();
      const goal = document.getElementById("sdg").value;
      const counts = {{}};
      sdgNames.forEach((pair) => {{ counts[pair[0]] = 0; }});
      const body = document.querySelector("#publications tbody");
      const allRows = Array.from(document.querySelectorAll("tbody tr[data-open]"));
      allRows.sort((a, b) => {{
        const aIndex = Number(a.dataset.index);
        const bIndex = Number(b.dataset.index);
        if (!sortKey) return aIndex - bIndex;
        return compareRows(rowRecord(aIndex), rowRecord(bIndex), sortKey, sortDir);
      }});
      allRows.forEach((tr) => body.appendChild(tr));
      const matched = [];
      allRows.forEach((tr) => {{
        const row = rows[Number(tr.dataset.index)];
        const yearOk = year === null || row.year === year;
        if (yearOk) {{
          (row.sdgs || []).forEach((item) => {{
            counts[item.number] = (counts[item.number] || 0) + 1;
          }});
        }}
        const goalOk = !goal || (row.sdgs || []).some((item) => String(item.number) === goal);
        if (yearOk && goalOk) matched.push(tr);
      }});
      const shown = matched.length;
      const size = pageSize();
      const pages = Math.max(1, Math.ceil(shown / size));
      if (page > pages) page = pages;
      if (page < 1) page = 1;
      const start = (page - 1) * size;
      const visible = new Set(matched.slice(start, start + size));
      document.querySelectorAll("tbody tr[data-open]").forEach((tr) => {{
        tr.hidden = !visible.has(tr);
      }});
      document.querySelectorAll("#sdg option").forEach((option) => {{
        if (!option.value) return;
        const pair = sdgNames.find((item) => String(item[0]) === option.value);
        option.textContent = pair[0] + " " + pair[1] + " (" + (counts[pair[0]] || 0) + ")";
      }});
      const noun = shown === 1 ? "publication" : "publications";
      const yearLabel = year === null ? "{YEARS[0]}–{YEARS[-1]}" : String(year);
      const goalLabel = goal ? document.querySelector("#sdg option:checked").textContent.replace(/ \\(\\d+\\)$/, "") : "";
      const whole = !goal && year === null;
      countEl.textContent = whole
        ? total + " " + (total === 1 ? "publication" : "publications") + " · " + yearLabel + " · snapshot {escape(built_at)}"
        : shown + " of " + total + " " + noun + " · " + yearLabel + (goalLabel ? " · " + goalLabel : "") + " · snapshot {escape(built_at)}";
      emptyEl.style.display = shown ? "none" : "block";
      footEl.hidden = shown === 0;
      const from = shown ? start + 1 : 0;
      const to = Math.min(start + size, shown);
      pageStatusEl.textContent = shown ? "Showing " + from + "–" + to + " of " + shown : "";
      if (shown) renderPager(pages);
    }}
    document.getElementById("sdg").addEventListener("change", () => {{
      closeModal();
      page = 1;
      applyFilters();
    }});
    document.getElementById("year").addEventListener("change", () => {{
      closeModal();
      page = 1;
      applyFilters();
    }});
    document.getElementById("page-size").addEventListener("change", () => {{
      closeModal();
      page = 1;
      applyFilters();
    }});
    document.querySelector("#publications thead").addEventListener("click", (event) => {{
      const th = event.target.closest("th[data-sort]");
      if (!th) return;
      if (sortKey === th.dataset.sort) sortDir = sortDir === "asc" ? "desc" : "asc";
      else {{
        sortKey = th.dataset.sort;
        sortDir = "asc";
      }}
      closeModal();
      page = 1;
      paintSort();
      applyFilters();
    }});
    pagerEl.addEventListener("click", (event) => {{
      const button = event.target.closest("button");
      if (!button || button.disabled) return;
      closeModal();
      if (button.dataset.step === "prev") page -= 1;
      else if (button.dataset.step === "next") page += 1;
      else if (button.dataset.page) page = Number(button.dataset.page);
      applyFilters();
    }});
    applyFilters();
    document.querySelector("#publications tbody").addEventListener("click", (event) => {{
      if (event.target.closest("a")) return;
      const row = event.target.closest("tr[data-open]");
      if (!row) return;
      openModal(Number(row.dataset.index));
    }});
    function applyFacultyYear() {{
      const year = document.getElementById("faculty-year").value;
      document.querySelectorAll("#faculty-table [data-year]").forEach((cell) => {{
        cell.hidden = year !== "" && cell.dataset.year !== year;
      }});
    }}
    document.getElementById("faculty-year").addEventListener("change", applyFacultyYear);
    document.querySelector(".site-nav").addEventListener("click", (event) => {{
      const button = event.target.closest("button[data-view]");
      if (!button) return;
      closeModal();
      ["kpi", "publication", "faculty"].forEach((name) => {{
        document.getElementById("view-" + name).hidden = name !== button.dataset.view;
      }});
      document.querySelectorAll(".site-nav button").forEach((item) => {{
        if (item === button) item.setAttribute("aria-current", "page");
        else item.removeAttribute("aria-current");
      }});
    }});
    document.addEventListener("keydown", (event) => {{
      if (event.key === "Escape") closeModal();
    }});
    document.getElementById("export-excel").addEventListener("click", () => CatalogExport.excel(rows));
    document.getElementById("export-pdf").addEventListener("click", () => CatalogExport.pdf(rows));
  </script>
</body>
</html>
"""


def main():
    works = fetch_works(BOUND_IDS | search_unchecked())
    rows = carry_indexes(build_rows(works))
    built_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    SITE.mkdir(exist_ok=True)
    snapshot = {
        "built_at": built_at,
        "publication_year": f"{YEARS[0]}-{YEARS[-1]}",
        "count": len(rows),
        "rows": rows,
    }
    (SITE / "snapshot.json").write_text(json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n")
    (SITE / "index.html").write_text(page(rows, built_at))
    print(f"wrote {len(rows)} publications to {SITE}")


if __name__ == "__main__":
    main()
