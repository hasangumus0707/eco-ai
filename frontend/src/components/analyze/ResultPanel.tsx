import { CircleCheck, Info, RotateCcw, TriangleAlert } from 'lucide-react'
import { CATEGORIES, CLASS_LABEL_TR } from '../../data/categories'
import type { PredictionResponse } from '../../types/api'
import { formatPercent } from '../../utils/image'
import { ProbabilityChart } from '../charts/ProbabilityChart'

interface Props {
  result: PredictionResponse
  imageSrc: string
  onReset: () => void
}

/** Analiz sonucunun tamamı: görsel, kategori, güven, grafik, kutu önerisi */
export function ResultPanel({ result, imageSrc, onReset }: Props) {
  const category = CATEGORIES.find((c) => c.id === result.predicted_class)
  const Icon = category?.icon

  return (
    <div className="animate-fade-up space-y-6">
      <div className="grid gap-6 lg:grid-cols-5">
        {/* Sol: fotoğraf + ana sonuç */}
        <div className="card overflow-hidden lg:col-span-2">
          <img src={imageSrc} alt="Analiz edilen atık" className="h-64 w-full bg-slate-100 object-contain dark:bg-slate-800" />
          <div className="p-6">
            {result.is_valid_prediction ? (
              <>
                <p className="flex items-center gap-1.5 text-sm font-semibold text-emerald-600 dark:text-emerald-400">
                  <CircleCheck className="size-4" /> Tahmin edilen kategori
                </p>
                <div className="mt-3 flex items-center gap-3">
                  {Icon && (
                    <span className={`grid size-12 place-items-center rounded-2xl ${category.accent}`}>
                      <Icon className="size-6" />
                    </span>
                  )}
                  <div>
                    <p className="text-2xl font-extrabold text-slate-900 dark:text-white">{result.predicted_class_tr}</p>
                    <p className="text-sm text-slate-500 dark:text-slate-400">{category?.nameEn}</p>
                  </div>
                </div>
              </>
            ) : (
              <UncertainNotice result={result} />
            )}

            <ConfidenceBar
              confidence={result.confidence}
              threshold={result.threshold}
              valid={result.is_valid_prediction}
              notRecyclable={result.reason === 'not_recyclable'}
            />
          </div>
        </div>

        {/* Sağ: olasılık dağılımı + kutu önerisi */}
        <div className="space-y-6 lg:col-span-3">
          <div className="card p-6">
            <h3 className="font-semibold text-slate-900 dark:text-white">Olasılık Dağılımı</h3>
            <p className="mb-2 text-sm text-slate-500 dark:text-slate-400">
              Modelin her kategori için hesapladığı olasılık (toplam %100)
            </p>
            <ProbabilityChart probabilities={result.probabilities} highlight={result.predicted_class} />
          </div>

          {result.is_valid_prediction && result.bin_name && (
            <div className="card p-6">
              <h3 className="font-semibold text-slate-900 dark:text-white">Önerilen Geri Dönüşüm Kutusu</h3>
              <div className="mt-4 flex items-center gap-4">
                <span
                  className="size-14 shrink-0 rounded-2xl shadow-inner ring-1 ring-black/10"
                  style={{ backgroundColor: result.bin_color_hex ?? undefined }}
                  aria-hidden
                />
                <div>
                  <p className="text-lg font-bold text-slate-900 dark:text-white">{result.bin_name}</p>
                  <p className="text-sm text-slate-500 dark:text-slate-400">Önerilen renk: {result.bin_color}</p>
                </div>
              </div>

              <h4 className="mt-6 text-sm font-semibold text-slate-900 dark:text-white">Nasıl ayrıştırılır?</h4>
              <ul className="mt-2 space-y-2">
                {result.recycling_advice.map((tip) => (
                  <li key={tip} className="flex gap-2 text-sm text-slate-600 dark:text-slate-300">
                    <CircleCheck className="mt-0.5 size-4 shrink-0 text-emerald-500" />
                    {tip}
                  </li>
                ))}
              </ul>

              <p className="mt-5 flex gap-2 rounded-xl bg-slate-50 p-3 text-xs text-slate-500 dark:bg-slate-800 dark:text-slate-400">
                <Info className="size-4 shrink-0" />
                {result.region_note}
              </p>
            </div>
          )}
        </div>
      </div>

      <div className="flex justify-center">
        <button className="btn-primary" onClick={onReset}>
          <RotateCcw className="size-4" /> Yeni Analiz Yap
        </button>
      </div>
    </div>
  )
}

function UncertainNotice({ result }: { result: PredictionResponse }) {
  const notRecyclable = result.reason === 'not_recyclable'
  return (
    <div className="rounded-2xl border border-amber-200 bg-amber-50 p-4 dark:border-amber-500/30 dark:bg-amber-500/10">
      <p className="flex items-center gap-2 font-semibold text-amber-800 dark:text-amber-200">
        <TriangleAlert className="size-5" />
        {notRecyclable ? 'Geri dönüştürülebilir atık tespit edilmedi' : 'Güvenilir sonuç verilemedi'}
      </p>
      <p className="mt-2 text-sm text-amber-800/90 dark:text-amber-100/80">{result.message}</p>
      {!notRecyclable && (
        <p className="mt-2 text-xs text-amber-700 dark:text-amber-200/70">
          Modelin en güçlü tahmini <strong>{CLASS_LABEL_TR[result.predicted_class]}</strong> idi, ancak güven skoru
          eşiğin altında kaldığı için kesin sonuç gösterilmiyor.
        </p>
      )}
    </div>
  )
}

interface ConfidenceBarProps {
  confidence: number
  threshold: number
  valid: boolean
  /** Model "diğer" dediyse burada gösterilen değer "diğer" sınıfının olasılığıdır */
  notRecyclable: boolean
}

function ConfidenceBar({ confidence, threshold, valid, notRecyclable }: ConfidenceBarProps) {
  return (
    <div className="mt-6">
      <div className="flex items-baseline justify-between">
        <span className="text-sm font-medium text-slate-600 dark:text-slate-300">
          {notRecyclable ? '“Atık değil” olasılığı' : 'Güven skoru'}
        </span>
        <span className={`text-2xl font-extrabold ${valid ? 'text-emerald-600 dark:text-emerald-400' : 'text-amber-600 dark:text-amber-400'}`}>
          {formatPercent(confidence)}
        </span>
      </div>
      <div className="relative mt-2 h-2.5 rounded-full bg-slate-100 dark:bg-slate-800">
        <div
          className={`h-full rounded-full transition-all duration-700 ${valid ? 'bg-emerald-500' : 'bg-amber-500'}`}
          style={{ width: `${confidence * 100}%` }}
        />
        {/* Eşik işareti (yalnızca atık tahminlerinde anlamlı) */}
        {!notRecyclable && <div className="absolute -top-1 h-4.5 w-0.5 bg-slate-500 dark:bg-slate-400" style={{ left: `${threshold * 100}%` }} title="Güven eşiği" />}
      </div>
      <p className="mt-1.5 text-xs text-slate-400 dark:text-slate-500">
        {notRecyclable
          ? 'Model bu görselin plastik, kâğıt, metal veya cam olmadığını düşünüyor.'
          : `Dikey çizgi: güven eşiği (${formatPercent(threshold)}). Bu değerin altındaki tahminler kesin sonuç olarak gösterilmez.`}
      </p>
    </div>
  )
}
