import { Leaf } from 'lucide-react'

export function Logo({ compact = false }: { compact?: boolean }) {
  return (
    <span className="flex items-center gap-2.5">
      <span className="grid size-9 place-items-center rounded-xl bg-gradient-to-br from-emerald-500 to-emerald-700 text-white shadow-md shadow-emerald-700/30">
        <Leaf className="size-5" strokeWidth={2.4} />
      </span>
      {!compact && (
        <span className="leading-tight">
          <span className="block text-lg font-extrabold tracking-tight text-emerald-900 dark:text-white">
            ECO <span className="text-emerald-600 dark:text-emerald-400">AI</span>
          </span>
          <span className="hidden text-[11px] font-medium text-slate-500 sm:block dark:text-slate-400">
            Akıllı Geri Dönüşüm Asistanı
          </span>
        </span>
      )}
    </span>
  )
}
