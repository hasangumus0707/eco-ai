import { Link } from 'react-router-dom'
import { Logo } from './Logo'

const YEAR = new Date().getFullYear()

export function Footer() {
  return (
    <footer className="mt-24 border-t border-emerald-100 bg-white dark:border-slate-800 dark:bg-slate-900">
      <div className="mx-auto grid max-w-6xl gap-8 px-4 py-10 sm:px-6 md:grid-cols-3">
        <div className="space-y-3">
          <Logo />
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Atık fotoğraflarını yapay zekâ ile sınıflandırarak doğru geri dönüşüm kutusuna yönlendiren bir üniversite
            dönem projesi.
          </p>
        </div>
        <div>
          <h3 className="mb-3 text-sm font-semibold text-slate-900 dark:text-white">Sayfalar</h3>
          <ul className="space-y-2 text-sm text-slate-500 dark:text-slate-400">
            <li><Link className="hover:text-emerald-700 dark:hover:text-emerald-400" to="/analiz">Atık Analizi</Link></li>
            <li><Link className="hover:text-emerald-700 dark:hover:text-emerald-400" to="/gecmis">Analiz Geçmişi</Link></li>
            <li><Link className="hover:text-emerald-700 dark:hover:text-emerald-400" to="/nasil-calisir">Nasıl Çalışır?</Link></li>
            <li><Link className="hover:text-emerald-700 dark:hover:text-emerald-400" to="/hakkinda">Proje Hakkında</Link></li>
          </ul>
        </div>
        <div>
          <h3 className="mb-3 text-sm font-semibold text-slate-900 dark:text-white">Teknoloji</h3>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            PyTorch · MobileNetV3 · FastAPI · React · TypeScript · Tailwind CSS
          </p>
          <p className="mt-3 text-xs text-slate-400 dark:text-slate-500">
            Tüm analizler kendi eğittiğimiz model ile yerel olarak yapılır; ücretli bir yapay zekâ servisi kullanılmaz.
          </p>
        </div>
      </div>
      <div className="border-t border-emerald-100 py-4 text-center text-xs text-slate-400 dark:border-slate-800 dark:text-slate-500">
        © {YEAR} ECO AI · Yapay Zekâ Dersi Dönem Projesi
      </div>
    </footer>
  )
}
