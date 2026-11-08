import { Component, type ErrorInfo, type ReactNode } from 'react'

interface Props {
  children: ReactNode
}
interface State {
  hasError: boolean
}

/**
 * Bir sayfada beklenmedik bir hata olursa bütün uygulama beyaz ekrana dönmesin;
 * kullanıcıya anlaşılır bir mesaj ve yenileme butonu gösterilsin.
 * (React'te hata sınırları yalnızca class bileşeni olarak yazılabilir.)
 */
export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false }

  static getDerivedStateFromError(): State {
    return { hasError: true }
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error('Arayüz hatası:', error, info.componentStack)
  }

  render() {
    if (!this.state.hasError) return this.props.children
    return (
      <div className="mx-auto max-w-md px-4 py-24 text-center">
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Bir şeyler ters gitti</h1>
        <p className="mt-2 text-slate-500 dark:text-slate-400">
          Bu sayfa yüklenirken beklenmedik bir hata oluştu. Sayfayı yenilemeyi deneyin.
        </p>
        <button className="btn-primary mt-8" onClick={() => window.location.reload()}>
          Sayfayı Yenile
        </button>
      </div>
    )
  }
}
