import { Menu, Moon, Sun, X } from 'lucide-react'
import { useState } from 'react'
import { Link, NavLink } from 'react-router-dom'
import { useThemeContext } from '../../hooks/ThemeContext'
import { Logo } from './Logo'

const LINKS = [
  { to: '/', label: 'Ana Sayfa' },
  { to: '/analiz', label: 'Analiz Et' },
  { to: '/gecmis', label: 'Geçmiş' },
  { to: '/nasil-calisir', label: 'Nasıl Çalışır?' },
  { to: '/hakkinda', label: 'Hakkında' },
]

function linkClass({ isActive }: { isActive: boolean }): string {
  return `rounded-full px-4 py-2 text-sm font-medium transition ${
    isActive
      ? 'bg-emerald-600 text-white'
      : 'text-slate-600 hover:bg-emerald-50 hover:text-emerald-800 dark:text-slate-300 dark:hover:bg-slate-800 dark:hover:text-white'
  }`
}

export function Navbar() {
  const { theme, toggle } = useThemeContext()
  const [open, setOpen] = useState(false)
  return (
    <header className="sticky top-0 z-40 border-b border-emerald-100/80 bg-white/80 backdrop-blur-md dark:border-slate-800 dark:bg-slate-950/80">
      <nav className="mx-auto flex h-16 max-w-6xl items-center justify-between px-4 sm:px-6">
        <Link to="/" aria-label="ECO AI ana sayfa">
          <Logo />
        </Link>

        <div className="hidden items-center gap-1 lg:flex">
          {LINKS.map((l) => (
            <NavLink key={l.to} to={l.to} end={l.to === '/'} className={linkClass}>
              {l.label}
            </NavLink>
          ))}
        </div>

        <div className="flex items-center gap-1">
          <button
            onClick={toggle}
            className="grid size-10 place-items-center rounded-full text-slate-600 transition hover:bg-emerald-50 dark:text-slate-300 dark:hover:bg-slate-800"
            aria-label={theme === 'dark' ? 'Açık temaya geç' : 'Karanlık temaya geç'}
            title={theme === 'dark' ? 'Açık tema' : 'Karanlık tema'}
          >
            {theme === 'dark' ? <Sun className="size-5" /> : <Moon className="size-5" />}
          </button>
          <button
            onClick={() => setOpen((o) => !o)}
            className="grid size-10 place-items-center rounded-full text-slate-600 transition hover:bg-emerald-50 lg:hidden dark:text-slate-300 dark:hover:bg-slate-800"
            aria-label="Menüyü aç/kapat"
            aria-expanded={open}
          >
            {open ? <X className="size-5" /> : <Menu className="size-5" />}
          </button>
        </div>
      </nav>

      {open && (
        <div className="border-t border-emerald-100 px-4 py-3 lg:hidden dark:border-slate-800">
          <div className="flex flex-col gap-1">
            {LINKS.map((l) => (
              // Bir bağlantıya tıklanınca mobil menüyü kapat
              <NavLink key={l.to} to={l.to} end={l.to === '/'} className={linkClass} onClick={() => setOpen(false)}>
                {l.label}
              </NavLink>
            ))}
          </div>
        </div>
      )}
    </header>
  )
}
