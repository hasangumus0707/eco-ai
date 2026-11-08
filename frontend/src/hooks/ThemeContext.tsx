import { createContext, useContext, type ReactNode } from 'react'
import { useTheme, type Theme } from './useTheme'

interface ThemeContextValue {
  theme: Theme
  toggle: () => void
}

const ThemeContext = createContext<ThemeContextValue | null>(null)

/** Temayı tüm uygulamaya dağıtır (navbar düğmesi ve grafik renkleri aynı değeri kullanır). */
export function ThemeProvider({ children }: { children: ReactNode }) {
  const value = useTheme()
  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>
}

// eslint-disable-next-line react-refresh/only-export-components
export function useThemeContext(): ThemeContextValue {
  const ctx = useContext(ThemeContext)
  if (!ctx) throw new Error('useThemeContext, ThemeProvider içinde kullanılmalı')
  return ctx
}
