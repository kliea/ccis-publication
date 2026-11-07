import { useState } from "react"

import { Pager } from "@/components/pager"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { ARTICLE_EACH_YEAR, FACULTY, YEARS } from "@/data/constants"
import { facultyCounts, type Row } from "@/lib/catalog"

export function FacultyView({ rows }: { rows: Row[] }) {
  const [year, setYear] = useState("all")
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState("5")
  const size = Number(pageSize)
  const pages = Math.max(1, Math.ceil(FACULTY.length / size))
  const current = Math.min(page, pages)
  const start = (current - 1) * size
  const visible = FACULTY.slice(start, start + size)
  const shownYears = year === "all" ? YEARS : [Number(year)]

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-semibold text-dusk">Faculty summary</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          {FACULTY.length} faculty. Each year requires at least {ARTICLE_EACH_YEAR} published articles. The year columns are Article - Accepted/Published for that year.
        </p>
      </div>
      <div className="flex flex-wrap items-center gap-2">
        <Label htmlFor="faculty-year">Year</Label>
        <Select value={year} onValueChange={setYear}>
          <SelectTrigger id="faculty-year" className="w-[140px]">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All</SelectItem>
            {YEARS.map((item) => (
              <SelectItem key={item} value={String(item)}>
                {item}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      <div className="rounded-xl border bg-card">
        <Table>
          <TableHeader>
            <TableRow className="bg-dusk hover:bg-dusk">
              <TableHead className="text-white">No.</TableHead>
              <TableHead className="text-white">Name</TableHead>
              <TableHead className="text-white">Rank</TableHead>
              <TableHead className="text-white">Department</TableHead>
              <TableHead className="text-right text-white">Req. Article</TableHead>
              {shownYears.map((item) => (
                <TableHead key={item} className="text-right text-white">
                  {item}
                </TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {visible.map((person, index) => {
              const counts = facultyCounts(rows, person.name)
              return (
                <TableRow key={person.name}>
                  <TableCell className="tabular-nums">{start + index + 1}</TableCell>
                  <TableCell className="font-medium">{person.name}</TableCell>
                  <TableCell>{person.rank}</TableCell>
                  <TableCell>{person.department}</TableCell>
                  <TableCell className="text-right tabular-nums">{ARTICLE_EACH_YEAR}</TableCell>
                  {shownYears.map((item) => (
                    <TableCell key={item} className="text-right tabular-nums">
                      {counts[item]}
                    </TableCell>
                  ))}
                </TableRow>
              )
            })}
          </TableBody>
        </Table>
      </div>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <p className="font-sans text-sm">
          Showing {start + 1}–{Math.min(start + size, FACULTY.length)} of {FACULTY.length}
        </p>
        <div className="ml-auto flex flex-wrap items-center gap-3">
          <Label htmlFor="faculty-page-size">Rows per page</Label>
          <Select
            value={pageSize}
            onValueChange={(value) => {
              setPageSize(value)
              setPage(1)
            }}
          >
            <SelectTrigger id="faculty-page-size" className="w-[88px]">
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
          <Pager page={current} pages={pages} onPage={setPage} label="Faculty pagination" />
        </div>
      </div>
    </div>
  )
}
