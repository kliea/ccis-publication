import { BOUND_IDS, ROSTER, SDGS, YEARS } from "@/data/constants"

export type Author = { name: string; roster: boolean }
export type Sdg = { number: number; name: string }
export type IndexId = "scopus" | "wos" | "aci"

export type Row = {
  id: string
  title: string
  authors: Author[]
  venue: string
  sponsor: string
  issn: string
  date: string
  year: number
  charge: string
  doi: string
  sdgs: Sdg[]
  indexes: string[]
}

export type NumberedRow = Row & { number: number }

export type Snapshot = {
  built_at: string
  publication_year: string
  count: number
  rows: Row[]
}

export type SortKey =
  | "number"
  | "authors"
  | "title"
  | "venue"
  | "sponsor"
  | "database"
  | "indexing"
  | "ranking"
  | "issn"
  | "status"
  | "date"
  | "charge"
  | "doi"

export type SortDir = "asc" | "desc"

const INDEX_NAMES: Record<string, string> = {
  scopus: "Scopus",
  wos: "Web of Science",
  aci: "Asian Citation Index",
}

const bound = new Set(BOUND_IDS)
const sdgNames = Object.fromEntries(SDGS.map((goal) => [goal.number, goal.name]))

export function yearSpan() {
  return `${YEARS[0]}–${YEARS[YEARS.length - 1]}`
}

export function tokens(name: string) {
  const folded = (name || "").normalize("NFD")
  return folded.replace(/[^A-Za-z\s]/g, " ").split(/\s+/).filter(Boolean)
}

export function authorFits(authorName: string, rosterName: string) {
  const author = tokens(authorName)
  const person = tokens(rosterName)
  if (author.length < 2 || person.length < 2) return false
  if (author[0].toLowerCase() !== person[0].toLowerCase()) return false
  if (author[author.length - 1].toLowerCase() !== person[person.length - 1].toLowerCase()) return false
  const middles = person.slice(1, -1)
  return author.slice(1, -1).every((part) => {
    const letter = part[0].toLowerCase()
    return middles.some((middle) => part.toLowerCase() === middle.toLowerCase() || letter === middle[0].toLowerCase())
  })
}

export function isRosterName(name: string) {
  return ROSTER.some((rosterName) => authorFits(name, rosterName))
}

export function authorOnRoster(name: string, authorId: string) {
  return bound.has(authorId) || isRosterName(name)
}

export function indexText(row: Pick<Row, "indexes">) {
  return (row.indexes || []).map((id) => INDEX_NAMES[id]).filter(Boolean).join("; ")
}

export function blankCount(part: number, whole: number) {
  if (!whole) return "0.0%"
  return `${((part / whole) * 100).toFixed(1)}%`
}

export function workKey(row: Pick<Row, "doi" | "id">) {
  if (row.doi) return `doi:${row.doi.replace(/\/+$/, "").toLowerCase()}`
  return `id:${row.id}`
}

export function catalogOrder(a: Row, b: Row) {
  const titleA = (a.title || "").toLocaleLowerCase()
  const titleB = (b.title || "").toLocaleLowerCase()
  if (titleA < titleB) return -1
  if (titleA > titleB) return 1
  const linkA = (a.doi || "").toLocaleLowerCase()
  const linkB = (b.doi || "").toLocaleLowerCase()
  const missingA = linkA ? 0 : 1
  const missingB = linkB ? 0 : 1
  if (missingA !== missingB) return missingA - missingB
  if (linkA < linkB) return -1
  if (linkA > linkB) return 1
  const dateA = a.date || "9999-99-99"
  const dateB = b.date || "9999-99-99"
  if (dateA < dateB) return -1
  if (dateA > dateB) return 1
  return 0
}

export function mergeRows(current: Row[], added: Row[]) {
  const next = current.slice()
  added.forEach((row) => {
    let index = 0
    while (index < next.length && catalogOrder(next[index], row) <= 0) index += 1
    next.splice(index, 0, row)
  })
  return next
}

export function latestDate(rows: Row[]) {
  let latest = ""
  rows.forEach((row) => {
    if (/^\d{4}-\d{2}-\d{2}$/.test(row.date || "") && row.date > latest) latest = row.date
  })
  return latest || `${YEARS[0]}-01-01`
}

export function normalizeRow(row: Row): Row {
  return {
    id: row.id || "",
    title: row.title || "",
    authors: row.authors || [],
    venue: row.venue || "",
    sponsor: row.sponsor || "",
    issn: row.issn || "",
    date: row.date || "",
    year: Number(row.year || 0),
    charge: row.charge || "",
    doi: row.doi || "",
    sdgs: row.sdgs || [],
    indexes: row.indexes || [],
  }
}

export function sdgName(number: number) {
  return sdgNames[number] || ""
}

function sortValue(row: NumberedRow, key: SortKey): string | number {
  if (key === "number") return row.number
  if (key === "authors") return (row.authors || []).map((author) => author.name).join(", ")
  if (key === "title") return row.title || ""
  if (key === "venue") return row.venue || ""
  if (key === "sponsor") return row.sponsor || ""
  if (key === "issn") return row.issn || ""
  if (key === "indexing") return indexText(row)
  if (key === "status") return "Published"
  if (key === "date") return row.date || ""
  if (key === "charge") return row.charge || ""
  if (key === "doi") return row.doi || ""
  return ""
}

export function compareRows(a: NumberedRow, b: NumberedRow, key: SortKey, dir: SortDir) {
  const av = sortValue(a, key)
  const bv = sortValue(b, key)
  const aBlank = av === "" || av == null
  const bBlank = bv === "" || bv == null
  if (aBlank && bBlank) return a.number - b.number
  if (aBlank) return 1
  if (bBlank) return -1
  let result = 0
  if (key === "number") result = Number(av) - Number(bv)
  else if (key === "charge") {
    const an = parseFloat(String(av).replace(/,/g, ""))
    const bn = parseFloat(String(bv).replace(/,/g, ""))
    result = !Number.isNaN(an) && !Number.isNaN(bn)
      ? an - bn
      : String(av).localeCompare(String(bv), undefined, { numeric: true, sensitivity: "base" })
  } else {
    result = String(av).localeCompare(String(bv), undefined, { numeric: true, sensitivity: "base" })
  }
  if (result === 0) return a.number - b.number
  return dir === "desc" ? -result : result
}

export function pageItems(current: number, total: number): Array<number | "ellipsis"> {
  if (total <= 7) return Array.from({ length: total }, (_, index) => index + 1)
  if (current <= 3) return [1, 2, 3, 4, "ellipsis", total]
  if (current >= total - 2) return [1, "ellipsis", total - 3, total - 2, total - 1, total]
  return [1, "ellipsis", current - 1, current, current + 1, "ellipsis", total]
}

export function facultyCounts(rows: Row[], name: string) {
  const counts: Record<number, number> = {}
  YEARS.forEach((year) => {
    counts[year] = 0
  })
  rows.forEach((row) => {
    if (!Object.prototype.hasOwnProperty.call(counts, row.year)) return
    if ((row.authors || []).some((author) => authorFits(author.name, name))) counts[row.year] += 1
  })
  return counts
}
