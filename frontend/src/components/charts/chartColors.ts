import type { Theme } from '../../hooks/useTheme'

/**
 * Grafik renkleri. Tek seri olduğu için tek bir vurgu rengi (yeşil) + nötr gri kullanılır.
 * Renkler dataviz doğrulayıcısıyla açık ve koyu zemin için ayrı ayrı kontrol edildi;
 * gri çubukların kontrastı düşük olduğu için her çubuğun değeri ayrıca yazı olarak gösterilir.
 */
export function chartColors(theme: Theme) {
  return theme === 'dark'
    ? { primary: '#10B981', muted: '#6B7280', grid: '#1F2937', text: '#C3C2B7', textStrong: '#F0EFEC', tooltipBg: '#0F172A', tooltipBorder: '#334155' }
    : { primary: '#059669', muted: '#9CA3AF', grid: '#E5E7EB', text: '#52514E', textStrong: '#0B0B0B', tooltipBg: '#FFFFFF', tooltipBorder: '#D1FAE5' }
}
