import { useEffect, useState } from "react"

import { FacultyView } from "@/components/faculty-view"
import { KpiView } from "@/components/kpi-view"
import { PublicationView } from "@/components/publication-view"
import { Card, CardContent } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { mergeRows, normalizeRow, type Row, type Snapshot } from "@/lib/catalog"
import { fetchRecent } from "@/lib/openalex"

const tabTrigger =
  "rounded-none border-b-2 border-transparent bg-transparent px-3 py-2 text-white shadow-none hover:text-orange data-[state=active]:border-orange data-[state=active]:bg-transparent data-[state=active]:text-white data-[state=active]:shadow-none"

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

  return (
    <Tabs defaultValue="publication">
      <header className="sticky top-0 z-20 border-b border-white/10 bg-dusk">
        <div className="mx-auto flex max-w-[1440px] flex-wrap items-center justify-between gap-3 px-4 py-3">
          <div className="flex items-center gap-2 font-sans font-semibold text-white">
            <span className="grid size-9 place-items-center rounded-full bg-white text-[10px] font-bold tracking-wide text-navy">CCIS</span>
            CCIS catalog
          </div>
          <TabsList className="h-auto gap-1 bg-transparent p-0">
            <TabsTrigger className={tabTrigger} value="kpi">KPI</TabsTrigger>
            <TabsTrigger className={tabTrigger} value="publication">Publication</TabsTrigger>
            <TabsTrigger className={tabTrigger} value="faculty">Faculty summary</TabsTrigger>
          </TabsList>
        </div>
      </header>
      <main className="mx-auto max-w-[1440px] px-4 py-8">
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
    </Tabs>
  )
}
