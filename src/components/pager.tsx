import { ChevronLeft, ChevronRight } from "lucide-react"

import { Button } from "@/components/ui/button"
import { pageItems } from "@/lib/catalog"

export function Pager({
  page,
  pages,
  onPage,
  label,
}: {
  page: number
  pages: number
  onPage: (page: number) => void
  label: string
}) {
  if (pages < 1) return null
  return (
    <nav aria-label={label}>
      <ul className="flex items-center gap-1">
        <li>
          <Button variant="ghost" size="icon" disabled={page <= 1} onClick={() => onPage(page - 1)} aria-label="Go to previous page">
            <ChevronLeft />
          </Button>
        </li>
        {pageItems(page, pages).map((item, index) => (
          <li key={item === "ellipsis" ? `ellipsis-${index}` : item}>
            {item === "ellipsis" ? (
              <span className="flex size-9 items-center justify-center text-muted-foreground" aria-hidden="true">
                …
              </span>
            ) : (
              <Button
                variant={item === page ? "default" : "ghost"}
                size="icon"
                className={item === page ? "bg-orange text-navy hover:bg-orange/90" : ""}
                aria-current={item === page ? "page" : undefined}
                aria-label={`Page ${item}`}
                onClick={() => onPage(item)}
              >
                {item}
              </Button>
            )}
          </li>
        ))}
        <li>
          <Button variant="ghost" size="icon" disabled={page >= pages} onClick={() => onPage(page + 1)} aria-label="Go to next page">
            <ChevronRight />
          </Button>
        </li>
      </ul>
    </nav>
  )
}
