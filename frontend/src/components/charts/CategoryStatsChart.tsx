import { Bar, BarChart, CartesianGrid, LabelList, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { CLASS_LABEL_TR } from '../../data/categories'
import { useThemeContext } from '../../hooks/ThemeContext'
import type { WasteClass } from '../../types/api'
import { chartColors } from './chartColors'

interface Props {
  counts: Record<WasteClass, number>
}

const ORDER: WasteClass[] = ['plastic', 'paper', 'metal', 'glass']

/** Geçmişteki güvenilir analizlerin kategori dağılımı (tek seri, dikey çubuklar) */
export function CategoryStatsChart({ counts }: Props) {
  const { theme } = useThemeContext()
  const c = chartColors(theme)
  const data = ORDER.map((cls) => ({ name: CLASS_LABEL_TR[cls], value: counts[cls] }))
  const max = Math.max(1, ...data.map((d) => d.value))

  return (
    <figure>
      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 24, right: 8, bottom: 4, left: -16 }} barCategoryGap="30%">
            <CartesianGrid vertical={false} stroke={c.grid} />
            <XAxis dataKey="name" tickLine={false} axisLine={false} tick={{ fill: c.text, fontSize: 13 }} />
            <YAxis
              allowDecimals={false}
              domain={[0, max]}
              tickLine={false}
              axisLine={false}
              tick={{ fill: c.text, fontSize: 12 }}
            />
            <Tooltip
              cursor={{ fill: c.grid, opacity: 0.5 }}
              formatter={(v) => [`${Number(v)} analiz`, 'Sayı']}
              contentStyle={{ background: c.tooltipBg, border: `1px solid ${c.tooltipBorder}`, borderRadius: 12, fontSize: 13 }}
              labelStyle={{ color: c.textStrong, fontWeight: 600 }}
              itemStyle={{ color: c.text }}
            />
            <Bar dataKey="value" fill={c.primary} radius={[4, 4, 0, 0]} maxBarSize={56} isAnimationActive={false}>
              <LabelList dataKey="value" position="top" style={{ fill: c.textStrong, fontSize: 12, fontWeight: 600 }} />
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
      <table className="sr-only">
        <caption>Kategorilere göre analiz sayısı</caption>
        <tbody>
          {data.map((d) => (
            <tr key={d.name}>
              <th>{d.name}</th>
              <td>{d.value}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </figure>
  )
}
