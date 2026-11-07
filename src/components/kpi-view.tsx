import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { YEAR_TARGET, YEARS } from "@/data/constants"
import { blankCount, type Row } from "@/lib/catalog"

const INDEXES = [
  ["scopus", "Scopus"],
  ["wos", "Web of Science (WoS)"],
  ["aci", "Asian Citation Index (ACI)"],
] as const

export function KpiView({ rows }: { rows: Row[] }) {
  const published: Record<number, number> = {}
  YEARS.forEach((year) => {
    published[year] = 0
  })
  const indexes = { scopus: 0, wos: 0, aci: 0 }
  rows.forEach((row) => {
    if (row.year in published) published[row.year] += 1
    ;(row.indexes || []).forEach((key) => {
      if (key in indexes) indexes[key as keyof typeof indexes] += 1
    })
  })
  const total = indexes.scopus + indexes.wos + indexes.aci

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-dusk">KPI</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Annual target is {YEAR_TARGET} published works for each year. % Target Achieved is that year&apos;s published works divided by {YEAR_TARGET}.
        </p>
      </div>
      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow className="bg-dusk hover:bg-dusk">
                <TableHead className="text-white">Year</TableHead>
                <TableHead className="text-right text-white">Total Articles</TableHead>
                <TableHead className="text-right text-white">Annual Target</TableHead>
                <TableHead className="text-right text-white">% Target Achieved</TableHead>
                <TableHead className="text-right text-white">Remaining Target</TableHead>
                <TableHead className="text-white">Performance Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {YEARS.map((year) => {
                const count = published[year]
                const remaining = Math.max(0, YEAR_TARGET - count)
                const achieved = count >= YEAR_TARGET
                return (
                  <TableRow key={year}>
                    <TableCell>{year}</TableCell>
                    <TableCell className="text-right tabular-nums">{count}</TableCell>
                    <TableCell className="text-right tabular-nums">{YEAR_TARGET}</TableCell>
                    <TableCell className="text-right tabular-nums">{blankCount(count, YEAR_TARGET)}</TableCell>
                    <TableCell className="text-right tabular-nums">{remaining}</TableCell>
                    <TableCell>
                      <Badge className={achieved ? "bg-orange text-navy" : ""} variant={achieved ? "default" : "secondary"}>
                        {achieved ? "Achieved" : "Below Target"}
                      </Badge>
                    </TableCell>
                  </TableRow>
                )
              })}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <CardTitle className="text-dusk">Indexing breakdown</CardTitle>
          <CardDescription>
            % Share is the database count divided by the sum of the three counts. A work listed in two databases is counted in each.
          </CardDescription>
        </CardHeader>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow className="bg-dusk hover:bg-dusk">
                <TableHead className="text-white">Indexing Database</TableHead>
                <TableHead className="text-right text-white">Total Count</TableHead>
                <TableHead className="text-right text-white">% Share</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {INDEXES.map(([key, label]) => (
                <TableRow key={key}>
                  <TableCell>{label}</TableCell>
                  <TableCell className="text-right tabular-nums">{indexes[key]}</TableCell>
                  <TableCell className="text-right tabular-nums">{blankCount(indexes[key], total)}</TableCell>
                </TableRow>
              ))}
              <TableRow className="bg-muted font-semibold hover:bg-muted">
                <TableCell>Total Indexed Articles</TableCell>
                <TableCell className="text-right tabular-nums">{total}</TableCell>
                <TableCell className="text-right tabular-nums">{blankCount(total, total)}</TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  )
}
