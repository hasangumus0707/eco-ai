import { useEffect } from 'react'
import { Outlet, useLocation } from 'react-router-dom'
import { ErrorBoundary } from '../ui/ErrorBoundary'
import { Footer } from './Footer'
import { Navbar } from './Navbar'

/** Tüm sayfaların ortak iskeleti: üst menü + sayfa içeriği + alt bilgi */
export function Layout() {
  const { pathname } = useLocation()

  // Sayfa değişince en üste kaydır.
  // Süslü parantez önemli: effect'ten değer döndürülmemeli (yeni tarayıcılarda scrollTo bir Promise döndürür).
  useEffect(() => {
    window.scrollTo({ top: 0 })
  }, [pathname])

  return (
    <div className="flex min-h-screen flex-col">
      <Navbar />
      <main className="flex-1">
        {/* key: sayfa değişince hata durumu sıfırlanır */}
        <ErrorBoundary key={pathname}>
          <Outlet />
        </ErrorBoundary>
      </main>
      <Footer />
    </div>
  )
}
