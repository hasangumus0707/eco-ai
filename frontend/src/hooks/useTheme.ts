import { useCallback, useEffect, useState } from 'react'
import { readString, writeString } from '../utils/storage'

export type Theme = 'light' | 'dark'
const STORAGE_KEY = 'eco-ai-theme'

function initialTheme(): Theme {
  const saved = readString(STORAGE_KEY)
  if (saved === 'light' || saved === 'dark') return saved
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

/** Açık/karanlık tema; seçim tarayıcıda hatırlanır. */
export function useTheme(): { theme: Theme; toggle: () => void } {
  const [theme, setTheme] = useState<Theme>(initialTheme)

  useEffect(() => {
    document.documentElement.classList.toggle('dark', theme === 'dark')
    writeString(STORAGE_KEY, theme)
  }, [theme])

  const toggle = useCallback(() => setTheme((t) => (t === 'dark' ? 'light' : 'dark')), [])
  return { theme, toggle }
}
