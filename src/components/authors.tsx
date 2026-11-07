import type { Author } from "@/lib/catalog"

export function Authors({ authors }: { authors: Author[] }) {
  return (
    <>
      {authors.map((author, index) => (
        <span key={`${author.name}-${index}`}>
          {index > 0 ? ", " : null}
          {author.roster ? <strong className="font-semibold text-navy">{author.name}</strong> : author.name}
        </span>
      ))}
    </>
  )
}

export function Empty() {
  return <span className="text-muted-foreground">—</span>
}
