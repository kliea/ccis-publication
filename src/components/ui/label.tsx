import * as React from "react"

import { cn } from "@/lib/utils"

function Label({ className, ...props }: React.ComponentProps<"label">) {
  return <label data-slot="label" className={cn("font-sans text-sm font-medium text-navy", className)} {...props} />
}

export { Label }
