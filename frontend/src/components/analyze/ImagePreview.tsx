import { Sparkles, X } from 'lucide-react'

interface Props {
  src: string
  fileName: string
  analyzing: boolean
  onRemove: () => void
  onAnalyze: () => void
}

/** Seçilen fotoğrafın önizlemesi; analiz sırasında tarama animasyonu gösterir. */
export function ImagePreview({ src, fileName, analyzing, onRemove, onAnalyze }: Props) {
  return (
    <div className="card overflow-hidden p-4 sm:p-6">
      <div className="relative mx-auto max-w-md overflow-hidden rounded-2xl bg-slate-100 dark:bg-slate-800">
        <img src={src} alt="Seçilen atık fotoğrafı" className="mx-auto max-h-[420px] w-full object-contain" />

        {analyzing && (
          <>
            <div className="absolute inset-0 bg-emerald-900/30" />
            {/* Yukarı-aşağı hareket eden tarama çizgisi */}
            <div className="absolute inset-x-0 h-1 animate-scan bg-emerald-300 shadow-[0_0_24px_6px] shadow-emerald-400/70" />
            <div className="absolute inset-x-0 bottom-4 flex justify-center">
              <span className="rounded-full bg-white/90 px-4 py-1.5 text-sm font-semibold text-emerald-800 dark:bg-slate-900/90 dark:text-emerald-300">
                Yapay zekâ analiz ediyor…
              </span>
            </div>
          </>
        )}

        {!analyzing && (
          <button
            onClick={onRemove}
            className="absolute top-3 right-3 grid size-9 place-items-center rounded-full bg-white/90 text-slate-700 shadow transition hover:bg-white dark:bg-slate-900/90 dark:text-slate-200"
            aria-label="Fotoğrafı kaldır"
            title="Fotoğrafı kaldır"
          >
            <X className="size-5" />
          </button>
        )}
      </div>

      <p className="mt-3 truncate text-center text-sm text-slate-500 dark:text-slate-400">{fileName}</p>

      <div className="mt-5 flex flex-wrap justify-center gap-3">
        <button className="btn-secondary" onClick={onRemove} disabled={analyzing}>
          Başka Fotoğraf Seç
        </button>
        <button className="btn-primary" onClick={onAnalyze} disabled={analyzing}>
          <Sparkles className="size-4" />
          {analyzing ? 'Analiz ediliyor…' : 'Yapay Zekâ ile Analiz Et'}
        </button>
      </div>
    </div>
  )
}
