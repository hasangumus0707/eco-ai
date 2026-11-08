import { CircleAlert, RotateCcw } from 'lucide-react'

interface Props {
  title?: string
  message: string
  onRetry?: () => void
}

export function ErrorAlert({ title = 'Bir sorun oluştu', message, onRetry }: Props) {
  return (
    <div
      role="alert"
      className="flex gap-3 rounded-2xl border border-red-200 bg-red-50 p-4 text-red-800 dark:border-red-500/30 dark:bg-red-500/10 dark:text-red-200"
    >
      <CircleAlert className="mt-0.5 size-5 shrink-0" />
      <div className="flex-1 space-y-2">
        <p className="font-semibold">{title}</p>
        <p className="text-sm">{message}</p>
        {onRetry && (
          <button
            onClick={onRetry}
            className="inline-flex items-center gap-1.5 text-sm font-semibold underline-offset-2 hover:underline"
          >
            <RotateCcw className="size-4" /> Tekrar dene
          </button>
        )}
      </div>
    </div>
  )
}
