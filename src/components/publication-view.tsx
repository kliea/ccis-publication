import { useMemo, useState, type ReactNode } from "react"
import { ArrowDown, ArrowUp, FileDown, FileSpreadsheet, RefreshCw } from "lucide-react"

import { Authors, Empty } from "@/components/authors"
import { Pager } from "@/components/pager"
import { Button } from "@/components/ui/button"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { SDGS, YEARS } from "@/data/constants"
import { compareRows, indexText, yearSpan, type NumberedRow, type Row, type SortDir, type SortKey } from "@/lib/catalog"
import { downloadExcel, downloadPdf } from "@/lib/export"

const COLUMNS: { key: SortKey; label: string }[] = [
  { key: "number", label: "No." },
  { key: "authors", label: "Author/s" },
  { key: "title", label: "Title" },
  { key: "venue", label: "Journal / Conference" },
  { key: "sponsor", label: "Sponsor / Publisher" },
  { key: "database", label: "Database" },
  { key: "indexing", label: "Indexing" },
  { key: "ranking", label: "Ranking / JIF" },
  { key: "issn", label: "ISSN / ISBN" },
  { key: "status", label: "Status" },
  { key: "date", label: "Date" },
  { key: "charge", label: "Publication Charge" },
  { key: "doi", label: "Link / DOI" },
]

function textOrEmpty(value: string) {
  return value ? value : <Empty />
}

export function PublicationView({
  rows,
  builtAt,
  refreshing,
  status,
  onRefresh,
}: {
  rows: Row[]
  builtAt: string
  refreshing: boolean
  status: string
  onRefresh: () => void
}) {
  const [year, setYear] = useState("all")
  const [sdg, setSdg] = useState("all")
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState("5")
  const [sortKey, setSortKey] = useState<SortKey | null>(null)
  const [sortDir, setSortDir] = useState<SortDir>("asc")
  const [open, setOpen] = useState<NumberedRow | null>(null)

  const numbered = useMemo(() => rows.map((row, index) => ({ ...row, number: index + 1 })), [rows])
  const yearCounts = useMemo(() => {
    const counts: Record<number, number> = {}
    YEARS.forEach((item) => {
      counts[item] = 0
    })
    numbered.forEach((row) => {
      if (row.year in counts) counts[row.year] += 1
    })
    return counts
  }, [numbered])
  const yearRows = useMemo(
    () => numbered.filter((row) => year === "all" || row.year === Number(year)),
    [numbered, year],
  )
  const sdgCounts = useMemo(() => {
    const counts: Record<number, number> = {}
    SDGS.forEach((goal) => {
      counts[goal.number] = 0
    })
    yearRows.forEach((row) => {
      row.sdgs.forEach((goal) => {
        counts[goal.number] = (counts[goal.number] || 0) + 1
      })
    })
    return counts
  }, [yearRows])
  const matched = useMemo(() => {
    const goal = sdg === "all" ? null : Number(sdg)
    const list = yearRows.filter((row) => !goal || row.sdgs.some((item) => item.number === goal))
    if (!sortKey) return list
    return [...list].sort((a, b) => compareRows(a, b, sortKey, sortDir))
  }, [yearRows, sdg, sortKey, sortDir])

  const size = Number(pageSize)
  const pages = Math.max(1, Math.ceil(matched.length / size) || 1)
  const current = matched.length ? Math.min(page, pages) : 1
  const start = (current - 1) * size
  const visible = matched.slice(start, start + size)
  const yearLabel = year === "all" ? yearSpan() : year
  const goalLabel = sdg === "all" ? "" : SDGS.find((goal) => String(goal.number) === sdg)?.name || ""
  const whole = year === "all" && sdg === "all"
  const noun = matched.length === 1 ? "publication" : "publications"
  const summary = whole
    ? `${numbered.length} ${numbered.length === 1 ? "publication" : "publications"} · ${yearLabel} · snapshot ${builtAt}`
    : `${matched.length} of ${numbered.length} ${noun} · ${yearLabel}${goalLabel ? ` · ${goalLabel}` : ""} · snapshot ${builtAt}`
  const fileStem = `publication-catalog-${year === "all" ? `${YEARS[0]}-${YEARS[YEARS.length - 1]}` : year}${sdg === "all" ? "" : `-sdg-${sdg}`}`

  function toggleSort(key: SortKey) {
    if (sortKey === key) setSortDir((dir) => (dir === "asc" ? "desc" : "asc"))
    else {
      setSortKey(key)
      setSortDir("asc")
    }
    setPage(1)
  }

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-semibold text-dusk">Publication catalog</h1>
        <p className="mt-1 text-sm">{summary}</p>
        <p className="mt-2 text-sm text-muted-foreground">
          Bold names are researchers on the roster. Choose a row for the full record. A link opens the work and leaves the table in place.
        </p>
      </div>
      <div className="flex flex-wrap items-center gap-2">
        <Label htmlFor="year">Year</Label>
        <Select
          value={year}
          onValueChange={(value) => {
            setYear(value)
            setPage(1)
          }}
        >
          <SelectTrigger id="year" className="w-[150px]">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All</SelectItem>
            {YEARS.map((item) => (
              <SelectItem key={item} value={String(item)}>
                {item} ({yearCounts[item]})
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Label htmlFor="sdg">SDG</Label>
        <Select
          value={sdg}
          onValueChange={(value) => {
            setSdg(value)
            setPage(1)
          }}
        >
          <SelectTrigger id="sdg" className="w-[min(100%,320px)]">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All</SelectItem>
            {SDGS.map((goal) => (
              <SelectItem key={goal.number} value={String(goal.number)}>
                {goal.number} {goal.name} ({sdgCounts[goal.number] || 0})
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Button onClick={onRefresh} disabled={refreshing}>
          <RefreshCw className={refreshing ? "animate-spin" : ""} />
          Refresh
        </Button>
        <Button variant="outline" onClick={() => downloadExcel(matched, fileStem)}>
          <FileSpreadsheet />
          Export Excel
        </Button>
        <Button variant="outline" onClick={() => downloadPdf(matched, fileStem, summary)}>
          <FileDown />
          Export PDF
        </Button>
      </div>
      <p className="min-h-5 font-sans text-sm text-muted-foreground" aria-live="polite">
        {status}
      </p>
      {matched.length === 0 ? <p>No publications for that year and goal.</p> : null}
      <div className="rounded-xl border bg-card">
        <Table>
          <caption className="sr-only">Published works recorded for {yearSpan()}.</caption>
          <TableHeader>
            <TableRow className="bg-dusk hover:bg-dusk">
              {COLUMNS.map((column) => {
                const active = sortKey === column.key
                return (
                  <TableHead
                    key={column.key}
                    aria-sort={active ? (sortDir === "asc" ? "ascending" : "descending") : "none"}
                    className="sticky top-0 bg-dusk p-0 text-white"
                  >
                    <button
                      type="button"
                      className="flex w-full items-center justify-between gap-2 px-3 py-2 text-left font-medium whitespace-nowrap hover:bg-white/10"
                      onClick={() => toggleSort(column.key)}
                    >
                      {column.label}
                      {active ? sortDir === "asc" ? <ArrowUp className="size-3.5" /> : <ArrowDown className="size-3.5" /> : <span className="size-3.5" />}
                    </button>
                  </TableHead>
                )
              })}
            </TableRow>
          </TableHeader>
          <TableBody>
            {visible.map((row) => (
              <TableRow
                key={row.id || row.doi || row.title}
                className="cursor-pointer hover:bg-muted/70"
                onClick={(event) => {
                  if ((event.target as HTMLElement).closest("a")) return
                  setOpen(row)
                }}
              >
                <TableCell className="tabular-nums">{row.number}</TableCell>
                <TableCell><Authors authors={row.authors} /></TableCell>
                <TableCell className="min-w-64">{textOrEmpty(row.title)}</TableCell>
                <TableCell className="min-w-40">{textOrEmpty(row.venue)}</TableCell>
                <TableCell>{textOrEmpty(row.sponsor)}</TableCell>
                <TableCell><Empty /></TableCell>
                <TableCell>{textOrEmpty(indexText(row))}</TableCell>
                <TableCell><Empty /></TableCell>
                <TableCell>{textOrEmpty(row.issn)}</TableCell>
                <TableCell>Published</TableCell>
                <TableCell className="whitespace-nowrap">{textOrEmpty(row.date)}</TableCell>
                <TableCell>{textOrEmpty(row.charge)}</TableCell>
                <TableCell className="max-w-56 break-all">
                  {row.doi ? (
                    <a className="text-dusk underline-offset-2 hover:text-orange hover:underline" href={row.doi}>
                      {row.doi}
                    </a>
                  ) : (
                    <Empty />
                  )}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
      {matched.length > 0 ? (
        <div className="flex flex-wrap items-center justify-between gap-3">
          <p className="font-sans text-sm">
            Showing {start + 1}–{Math.min(start + size, matched.length)} of {matched.length}
          </p>
          <div className="ml-auto flex flex-wrap items-center gap-3">
            <Label htmlFor="page-size">Rows per page</Label>
            <Select
              value={pageSize}
              onValueChange={(value) => {
                setPageSize(value)
                setPage(1)
              }}
            >
              <SelectTrigger id="page-size" className="w-[88px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {["5", "10", "25", "50"].map((value) => (
                  <SelectItem key={value} value={value}>
                    {value}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Pager page={current} pages={pages} onPage={setPage} label="pagination" />
          </div>
        </div>
      ) : null}
      <Dialog open={open !== null} onOpenChange={(next) => { if (!next) setOpen(null) }}>
        <DialogContent>
          {open ? (
            <>
              <DialogHeader>
                <DialogTitle>{open.title || "Publication"}</DialogTitle>
                <DialogDescription>
                  {open.date || "Published"}{open.venue ? ` · ${open.venue}` : ""}
                </DialogDescription>
              </DialogHeader>
              <dl className="font-sans text-sm">
                <Detail label="No." value={String(open.number)} />
                <Detail label="Author/s" value={<Authors authors={open.authors} />} />
                <Detail label="Title" value={textOrEmpty(open.title)} />
                <Detail label="Journal / Conference" value={textOrEmpty(open.venue)} />
                <Detail label="Sponsor / Publisher" value={textOrEmpty(open.sponsor)} />
                <Detail label="Database" value={<Empty />} />
                <Detail label="Indexing" value={textOrEmpty(indexText(open))} />
                <Detail label="Ranking / JIF" value={<Empty />} />
                <Detail label="ISSN / ISBN" value={textOrEmpty(open.issn)} />
                <Detail label="Status" value="Published" />
                <Detail label="Date" value={textOrEmpty(open.date)} />
                <Detail label="Year" value={textOrEmpty(String(open.year || ""))} />
                <Detail label="Publication Charge" value={textOrEmpty(open.charge)} />
                <Detail
                  label="Link / DOI"
                  value={open.doi ? <a className="text-dusk underline-offset-2 hover:underline" href={open.doi}>{open.doi}</a> : <Empty />}
                />
                <Detail
                  label="SDG"
                  value={open.sdgs.length ? open.sdgs.map((goal) => `${goal.number} ${goal.name}`).join("; ") : <Empty />}
                />
              </dl>
            </>
          ) : null}
        </DialogContent>
      </Dialog>
    </div>
  )
}

function Detail({ label, value }: { label: string; value: ReactNode }) {
  return (
    <div className="grid grid-cols-[180px_1fr] gap-3 border-b py-2">
      <dt className="text-muted-foreground">{label}</dt>
      <dd>{value}</dd>
    </div>
  )
}
