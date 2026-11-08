import { useEffect, useState } from "react"

import { FacultyView } from "@/components/faculty-view"
import { KpiView } from "@/components/kpi-view"
import { PublicationView } from "@/components/publication-view"
import { Card, CardContent } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { YEAR_TARGET, YEARS } from "@/data/constants"
import { mergeRows, normalizeRow, yearSpan, type Row, type Snapshot } from "@/lib/catalog"
import { fetchRecent } from "@/lib/openalex"

const tabTrigger =
  "rounded-full px-4 py-1.5 text-cream/90 shadow-none hover:text-cream data-[state=active]:bg-ink data-[state=active]:text-cream data-[state=active]:shadow-none"

export function App() {
  const [rows, setRows] = useState<Row[] | null>(null)
  const [builtAt, setBuiltAt] = useState("")
  const [error, setError] = useState("")
  const [refreshing, setRefreshing] = useState(false)
  const [status, setStatus] = useState("")

  useEffect(() => {
    let active = true
    fetch("/snapshot.json")
      .then((response) => {
        if (!response.ok) throw new Error("Could not load the catalog")
        return response.json() as Promise<Snapshot>
      })
      .then((snapshot) => {
        if (!active) return
        setRows((snapshot.rows || []).map(normalizeRow))
        setBuiltAt(snapshot.built_at || "")
      })
      .catch(() => {
        if (active) setError("Could not load the catalog.")
      })
    return () => {
      active = false
    }
  }, [])

  async function refresh() {
    if (!rows || refreshing) return
    setRefreshing(true)
    setStatus("Fetching recent publications…")
    try {
      const { added, fromDate } = await fetchRecent(rows)
      if (!added.length) {
        setStatus(`No additional recent publications since ${fromDate}.`)
        return
      }
      setRows((current) => mergeRows(current || [], added))
      const noun = added.length === 1 ? "publication" : "publications"
      setStatus(`Added ${added.length} recent ${noun}.`)
    } catch (error) {
      console.error(error)
      setStatus("Refresh failed. Try again.")
    } finally {
      setRefreshing(false)
    }
  }

  const counts = yearCounts(rows)
  const latestYear = YEARS[YEARS.length - 1]
  const total = rows?.length ?? 0
  const peak = Math.max(...YEARS.map((year) => counts[year]), 1)

  return (
    <Tabs defaultValue="publication">
      <div className="min-h-screen bg-orange p-3 sm:p-6">
        <div className="mx-auto max-w-[1440px] overflow-hidden rounded-[28px] bg-ink shadow-[0_30px_80px_rgba(33,19,15,0.35)]">
          <section className="relative bg-[linear-gradient(160deg,#F87F23_0%,#e45416_42%,#CC0A0D_100%)] px-5 py-6 text-cream sm:px-8 sm:py-8">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <div className="flex items-center gap-2 font-sans font-semibold">
                <span className="grid size-9 place-items-center rounded-full bg-cream text-[10px] font-bold tracking-wide text-ink">CCIS</span>
                CCIS catalog
              </div>
              <TabsList className="h-auto rounded-full bg-ink/25 p-1">
                <TabsTrigger className={tabTrigger} value="kpi">KPI</TabsTrigger>
                <TabsTrigger className={tabTrigger} value="publication">Publication</TabsTrigger>
                <TabsTrigger className={tabTrigger} value="faculty">Faculty summary</TabsTrigger>
              </TabsList>
            </div>
            <div className="mt-10 flex flex-wrap items-end justify-between gap-8">
              <div>
                <p className="font-sans text-sm tracking-wide text-cream/80">Published works</p>
                <p className="mt-1 font-serif text-6xl leading-none tracking-tight sm:text-7xl">{total || "—"}</p>
                <p className="mt-3 font-sans text-sm text-cream/80">
                  {yearSpan()}{builtAt ? ` · snapshot ${builtAt}` : ""}
                </p>
              </div>
              <div className="w-full max-w-[220px] rounded-2xl border border-cream/25 bg-ink/25 p-4 font-sans backdrop-blur-sm">
                <p className="text-xs text-cream/75">{latestYear} against the target of {YEAR_TARGET}</p>
                <p className="mt-1 text-3xl font-semibold">{counts[latestYear]}</p>
                <div className="mt-4 flex h-14 items-end gap-2" aria-hidden="true">
                  {YEARS.map((year) => (
                    <div
                      key={year}
                      className="flex-1 rounded-sm bg-cream"
                      style={{ height: `${Math.max(8, Math.round((counts[year] / peak) * 56))}px` }}
                    />
                  ))}
                </div>
              </div>
            </div>
            <div className="mt-10">
              <p className="font-sans text-sm text-cream/80">Our progress</p>
              <ol className="relative mt-5 grid grid-cols-4 gap-2">
                <span className="absolute top-4 right-[12%] left-[12%] h-px bg-cream/45" />
                {YEARS.map((year) => {
                  const met = counts[year] >= YEAR_TARGET
                  return (
                    <li key={year} className="relative flex flex-col items-center gap-2 text-center">
                      <span className={`grid size-8 place-items-center rounded-full font-sans text-xs font-semibold ${met ? "bg-cream text-ink" : "border border-cream/70 bg-red text-cream"}`}>
                        {String(year).slice(2)}
                      </span>
                      <span className="font-sans text-xs text-cream/80">{year}</span>
                      <span className="font-sans text-sm font-semibold">{counts[year]}</span>
                    </li>
                  )
                })}
              </ol>
            </div>
          </section>
          <main className="bg-cream px-4 py-8 text-ink sm:px-8">
            {error ? (
              <Card>
                <CardContent className="py-6">{error}</CardContent>
              </Card>
            ) : rows === null ? (
              <Card>
                <CardContent className="py-6 font-sans text-sm text-muted-foreground">Loading catalog…</CardContent>
              </Card>
            ) : (
              <>
                <TabsContent forceMount className="data-[state=inactive]:hidden" value="kpi">
                  <KpiView rows={rows} />
                </TabsContent>
                <TabsContent forceMount className="data-[state=inactive]:hidden" value="publication">
                  <PublicationView rows={rows} builtAt={builtAt} refreshing={refreshing} status={status} onRefresh={refresh} />
                </TabsContent>
                <TabsContent forceMount className="data-[state=inactive]:hidden" value="faculty">
                  <FacultyView rows={rows} />
                </TabsContent>
              </>
            )}
          </main>
        </div>
      </div>
    </Tabs>
  )
}

function yearCounts(rows: Row[] | null) {
  const counts: Record<number, number> = {}
  YEARS.forEach((year) => {
    counts[year] = 0
  })
  rows?.forEach((row) => {
    if (row.year in counts) counts[row.year] += 1
  })
  return counts
}
