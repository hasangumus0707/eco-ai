import { Calendar, CircleCheck, History, ScanSearch, Trash2, TriangleAlert } from 'lucide-react'
import { useState, type ReactNode } from 'react'
import { Link } from 'react-router-dom'
import { CategoryStatsChart } from '../components/charts/CategoryStatsChart'
import { PageHeader } from '../components/ui/PageHeader'
import { CLASS_LABEL_TR } from '../data/categories'
import { useHistory, useHistoryStats } from '../hooks/useHistory'
import { historyStore, type HistoryEntry } from '../services/historyStore'
import { formatPercent } from '../utils/image'

export function HistoryPage() {
  const history = useHistory()
  const stats = useHistoryStats()
  const [confirmClear, setConfirmClear] = useState(false)

  return (
    <div className="mx-auto max-w-5xl px-4 pb-8 sm:px-6">
      <PageHeader
        eyebrow="Analiz Geçmişi"
        title="Önceki Analizlerin"
        description="Bu tarayıcıda yaptığınız analizler burada saklanır. Veriler yalnızca bu cihazda tutulur, sunucuya kaydedilmez."
      />

      {history.length === 0 ? (
        <div className="card mx-auto max-w-lg p-10 text-center">
          <History className="mx-auto size-12 text-emerald-300 dark:text-slate-600" />
          <p className="mt-4 font-semibold text-slate-900 dark:text-white">Henüz analiz yapılmadı</p>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">İlk analizinizi yaptığınızda sonuçlar burada görünecek.</p>
          <Link to="/analiz" className="btn-primary mt-6">
            <ScanSearch className="size-4" /> İlk Analizi Yap
          </Link>
        </div>
      ) : (
        <div className="space-y-6">
          {/* İstatistik kutucukları */}
          <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
            <StatTile label="Toplam analiz" value={stats.total} />
            <StatTile label="Bugünkü analiz" value={stats.today} icon={<Calendar className="size-4" />} />
            <StatTile label="Güvenilir sonuç" value={stats.valid} icon={<CircleCheck className="size-4 text-emerald-500" />} />
            <StatTile label="Belirsiz / atık değil" value={stats.uncertain} icon={<TriangleAlert className="size-4 text-amber-500" />} />
          </div>

          {/* Kategori grafiği */}
          <div className="card p-6">
            <h2 className="font-semibold text-slate-900 dark:text-white">Kategorilere Göre Analizler</h2>
            <p className="mb-4 text-sm text-slate-500 dark:text-slate-400">Yalnızca güvenilir (kesin) sonuçlar sayılır</p>
            {stats.valid > 0 ? (
              <CategoryStatsChart counts={stats.byClass} />
            ) : (
              <p className="py-10 text-center text-sm text-slate-400">Henüz güvenilir sonuç yok.</p>
            )}
          </div>

          {/* Liste */}
          <div className="card p-4 sm:p-6">
            <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
              <h2 className="font-semibold text-slate-900 dark:text-white">Son {history.length} analiz</h2>
              {confirmClear ? (
                <div className="flex items-center gap-2 text-sm">
                  <span className="text-slate-600 dark:text-slate-300">Tüm geçmiş silinsin mi?</span>
                  <button
                    onClick={() => {
                      historyStore.clear()
                      setConfirmClear(false)
                    }}
                    className="rounded-full bg-red-600 px-3 py-1.5 font-semibold text-white hover:bg-red-700"
                  >
                    Evet, sil
                  </button>
                  <button onClick={() => setConfirmClear(false)} className="rounded-full px-3 py-1.5 font-semibold text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800">
                    Vazgeç
                  </button>
                </div>
              ) : (
                <button onClick={() => setConfirmClear(true)} className="inline-flex items-center gap-1.5 text-sm font-medium text-red-600 hover:underline dark:text-red-400">
                  <Trash2 className="size-4" /> Geçmişi temizle
                </button>
              )}
            </div>
            <ul className="divide-y divide-emerald-50 dark:divide-slate-800">
              {history.map((e) => (
                <HistoryRow key={e.id} entry={e} />
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  )
}

function HistoryRow({ entry }: { entry: HistoryEntry }) {
  const date = new Date(entry.createdAt).toLocaleString('tr-TR', { dateStyle: 'medium', timeStyle: 'short' })
  return (
    <li className="flex items-center gap-4 py-3">
      {entry.thumbnail ? (
        <img src={entry.thumbnail} alt="" className="size-14 shrink-0 rounded-xl object-cover" />
      ) : (
        <span className="size-14 shrink-0 rounded-xl bg-slate-100 dark:bg-slate-800" />
      )}
      <div className="min-w-0 flex-1">
        <p className="flex items-center gap-2 font-semibold text-slate-900 dark:text-white">
          {entry.isValid ? (
            <>
              {entry.binColorHex && <span className="size-2.5 rounded-full ring-1 ring-black/10" style={{ backgroundColor: entry.binColorHex }} />}
              {entry.predictedClassTr}
            </>
          ) : (
            <span className="text-amber-700 dark:text-amber-300">
              {entry.reason === 'not_recyclable' ? 'Atık tespit edilmedi' : `Belirsiz (en yakın: ${CLASS_LABEL_TR[entry.predictedClass]})`}
            </span>
          )}
        </p>
        <p className="text-xs text-slate-500 dark:text-slate-400">
          {date} · güven {formatPercent(entry.confidence)}
        </p>
      </div>
      <button
        onClick={() => historyStore.remove(entry.id)}
        className="grid size-9 shrink-0 place-items-center rounded-full text-slate-400 transition hover:bg-red-50 hover:text-red-600 dark:hover:bg-red-500/10"
        aria-label="Bu kaydı sil"
        title="Sil"
      >
        <Trash2 className="size-4" />
      </button>
    </li>
  )
}

function StatTile({ label, value, icon }: { label: string; value: number; icon?: ReactNode }) {
  return (
    <div className="card p-5">
      <p className="flex items-center gap-1.5 text-sm text-slate-500 dark:text-slate-400">
        {icon}
        {label}
      </p>
      <p className="mt-2 text-3xl font-extrabold text-slate-900 dark:text-white">{value.toLocaleString('tr-TR')}</p>
    </div>
  )
}
