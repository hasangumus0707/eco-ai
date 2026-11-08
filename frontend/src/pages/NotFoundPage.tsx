import { Link } from 'react-router-dom'

export function NotFoundPage() {
  return (
    <div className="mx-auto max-w-md px-4 py-24 text-center">
      <p className="text-6xl font-black text-emerald-200 dark:text-slate-700">404</p>
      <h1 className="mt-4 text-2xl font-bold text-slate-900 dark:text-white">Sayfa bulunamadı</h1>
      <p className="mt-2 text-slate-500 dark:text-slate-400">Aradığınız sayfa taşınmış veya hiç var olmamış olabilir.</p>
      <Link to="/" className="btn-primary mt-8">
        Ana Sayfaya Dön
      </Link>
    </div>
  )
}
