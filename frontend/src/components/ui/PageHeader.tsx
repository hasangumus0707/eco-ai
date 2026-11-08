import type { ReactNode } from 'react'

interface Props {
  eyebrow?: string
  title: string
  description?: ReactNode
}

/** Alt sayfaların üst başlık alanı */
export function PageHeader({ eyebrow, title, description }: Props) {
  return (
    <div className="mx-auto max-w-3xl animate-fade-up px-4 pt-12 pb-8 text-center sm:pt-16">
      {eyebrow && (
        <p className="mb-3 text-sm font-semibold tracking-wider text-emerald-600 uppercase dark:text-emerald-400">
          {eyebrow}
        </p>
      )}
      <h1 className="text-3xl font-extrabold tracking-tight text-emerald-950 sm:text-4xl dark:text-white">{title}</h1>
      {description && <p className="mt-4 text-lg text-slate-600 dark:text-slate-400">{description}</p>}
    </div>
  )
}
