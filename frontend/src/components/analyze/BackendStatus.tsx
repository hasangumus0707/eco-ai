import { RotateCcw } from 'lucide-react'
import type { ReactNode } from 'react'
import { useBackendHealth } from '../../hooks/useBackendHealth'
import { formatPercent } from '../../utils/image'

/**
 * Backend ve model durumunu gösteren küçük rozet.
 * Model dosyasının parmak izini (sha256) göstererek gerçek modelin çalıştığını kanıtlar.
 */
export function BackendStatus() {
  const health = useBackendHealth()

  if (health.status === 'checking') {
    return <Badge dot="bg-amber-400 animate-pulse">Yapay zekâ sunucusu kontrol ediliyor…</Badge>
  }

  if (health.status === 'offline') {
    return (
      <Badge dot="bg-red-500">
        Sunucuya ulaşılamıyor
        <button onClick={health.retry} className="ml-2 inline-flex items-center gap-1 font-semibold underline-offset-2 hover:underline">
          <RotateCcw className="size-3" /> Tekrar dene
        </button>
      </Badge>
    )
  }

  const d = health.data
  return (
    <Badge dot="bg-emerald-500">
      Model hazır: <strong className="font-semibold">{d.model_arch}</strong>
      <span className="hidden sm:inline">
        {' '}· test doğruluğu {formatPercent(d.test_accuracy)} · {d.device.toUpperCase()} ·{' '}
        <span title="Model dosyasının parmak izi">#{d.model_sha256}</span>
      </span>
    </Badge>
  )
}

function Badge({ dot, children }: { dot: string; children: ReactNode }) {
  return (
    <div className="inline-flex items-center gap-2 rounded-full border border-emerald-100 bg-white px-4 py-1.5 text-xs text-slate-600 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-300">
      <span className={`size-2 rounded-full ${dot}`} />
      <span>{children}</span>
    </div>
  )
}
