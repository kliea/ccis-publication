import { BOUND_IDS, MAILTO, YEARS } from "@/data/constants"
import { authorOnRoster, latestDate, sdgName, workKey, type Row } from "@/lib/catalog"

type Money = { value?: number | null; currency?: string | null }

type OpenAlexWork = {
  id?: string
  title?: string
  display_name?: string
  publication_date?: string
  publication_year?: number
  doi?: string
  authorships?: Array<{
    raw_author_name?: string
    author?: { id?: string; display_name?: string }
  }>
  funders?: Array<{ display_name?: string } | null>
  primary_location?: {
    source?: {
      display_name?: string
      host_organization_name?: string
      issn_l?: string
      issn?: string[]
    } | null
  } | null
  apc_paid?: Money | null
  apc_list?: Money | null
  sustainable_development_goals?: Array<{ id?: string }>
}

function openalexId(value?: string) {
  if (!value) return ""
  const text = String(value).replace(/\/+$/, "")
  return text.slice(text.lastIndexOf("/") + 1)
}

function money(amount?: Money | null) {
  if (!amount || amount.value == null) return ""
  let value: number | string = amount.value
  if (typeof value === "number" && Math.abs(value - Math.round(value)) < 1e-9) value = Math.round(value)
  return `${value} ${amount.currency || ""}`.trim()
}

function rowFrom(work: OpenAlexWork): Row {
  const source = work.primary_location?.source || {}
  const authors = (work.authorships || []).flatMap((authorship) => {
    const author = authorship.author || {}
    const name = authorship.raw_author_name || author.display_name || ""
    if (!name) return []
    const authorId = openalexId(author.id)
    return [{ name, roster: authorOnRoster(name, authorId) }]
  })
  const funders: string[] = []
  ;(work.funders || []).forEach((funder) => {
    const name = funder?.display_name
    if (name && !funders.includes(name)) funders.push(name)
  })
  const publisher = source.host_organization_name || ""
  let sponsor = publisher || funders.join("; ")
  if (publisher && funders.length) sponsor = `${publisher}; ${funders.join("; ")}`
  const issns = source.issn || []
  const goals: Row["sdgs"] = []
  const seen = new Set<number>()
  ;(work.sustainable_development_goals || []).forEach((goal) => {
    const number = Number(openalexId(goal.id) || 0)
    if (!sdgName(number) || seen.has(number)) return
    seen.add(number)
    goals.push({ number, name: sdgName(number) })
  })
  goals.sort((a, b) => a.number - b.number)
  const year = Number(work.publication_year || 0)
  return {
    id: openalexId(work.id),
    title: work.title || work.display_name || "",
    authors,
    venue: source.display_name || "",
    sponsor,
    issn: source.issn_l || (issns.length ? issns[0] : ""),
    date: work.publication_date || String(work.publication_year || ""),
    year,
    charge: money(work.apc_paid) || money(work.apc_list),
    doi: typeof work.doi === "string" ? work.doi : "",
    sdgs: goals,
    indexes: [],
  }
}

async function fetchWorks(fromDate: string) {
  const works: OpenAlexWork[] = []
  const seen = new Set<string>()
  for (let start = 0; start < BOUND_IDS.length; start += 20) {
    const batch = BOUND_IDS.slice(start, start + 20)
    let page = 1
    while (page <= 10) {
      const filter = [
        `authorships.author.id:${batch.join("|")}`,
        `from_publication_date:${fromDate}`,
        `publication_year:${YEARS[0]}-${YEARS[YEARS.length - 1]}`,
      ].join(",")
      const params = new URLSearchParams({
        filter,
        sort: "publication_date:desc",
        per_page: "200",
        page: String(page),
        mailto: MAILTO,
      })
      const response = await fetch(`https://api.openalex.org/works?${params.toString()}`)
      if (!response.ok) throw new Error(`OpenAlex returned ${response.status}`)
      const payload = (await response.json()) as { results?: OpenAlexWork[]; meta?: { count?: number } }
      const results = payload.results || []
      results.forEach((work) => {
        const id = work.id || ""
        if (!id || seen.has(id)) return
        seen.add(id)
        works.push(work)
      })
      const count = payload.meta?.count || 0
      if (!results.length || page * 200 >= count) break
      page += 1
    }
  }
  return works
}

export async function fetchRecent(rows: Row[]) {
  const fromDate = latestDate(rows)
  const works = await fetchWorks(fromDate)
  const known = new Set(rows.map(workKey))
  const added: Row[] = []
  works.forEach((work) => {
    const row = rowFrom(work)
    if (row.year < YEARS[0] || row.year > YEARS[YEARS.length - 1]) return
    const key = workKey(row)
    if (known.has(key)) return
    known.add(key)
    added.push(row)
  })
  return { added, fromDate }
}
