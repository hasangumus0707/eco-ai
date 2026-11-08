import { Bar, BarChart, Cell, LabelList, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { CLASS_LABEL_TR, CLASS_ORDER } from '../../data/categories'
import { useThemeContext } from '../../hooks/ThemeContext'
import type { ModelClass } from '../../types/api'
import { formatPercent } from '../../utils/image'
import { chartColors } from './chartColors'

interface Props {
  probabilities: Record<ModelClass, number>
  highlight: ModelClass
}

/**
 * Modelin her sınıfa verdiği olasılığı yatay çubuklarla gösterir.
 * Tahmin edilen sınıf yeşil, diğerleri gri. Değerler çubukların yanında yazılıdır.
 */
export function ProbabilityChart({ probabilities, highlight }: Props) {
  const { theme } = useThemeContext()
  const c = chartColors(theme)
  const data = CLASS_ORDER.map((cls) => ({ cls, name: CLASS_LABEL_TR[cls], value: probabilities[cls] ?? 0 }))

  return (
    <figure>
      <div className="h-56 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} layout="vertical" margin={{ top: 4, right: 56, bottom: 4, left: 4 }} barCategoryGap={6}>
            <XAxis type="number" domain={[0, 1]} hide />
            <YAxis
              type="category"
              dataKey="name"
              width={64}
              tickLine={false}
              axisLine={false}
              tick={{ fill: c.text, fontSize: 13 }}
            />
            <Tooltip
              cursor={{ fill: c.grid, opacity: 0.5 }}
              formatter={(v) => [formatPercent(Number(v)), 'Olasılık']}
              contentStyle={{ background: c.tooltipBg, border: `1px solid ${c.tooltipBorder}`, borderRadius: 12, fontSize: 13 }}
              labelStyle={{ color: c.textStrong, fontWeight: 600 }}
              itemStyle={{ color: c.text }}
            />
            {/* Animasyon kapalı: Recharts değer etiketlerini animasyon bitene kadar göstermiyor */}
            <Bar dataKey="value" radius={[0, 4, 4, 0]} minPointSize={2} isAnimationActive={false}>
              {data.map((d) => (
                <Cell key={d.cls} fill={d.cls === highlight ? c.primary : c.muted} />
              ))}
              <LabelList
                dataKey="value"
                position="right"
                formatter={(v) => formatPercent(Number(v))}
                style={{ fill: c.textStrong, fontSize: 12, fontWeight: 600 }}
              />
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
      {/* Ekran okuyucular için tablo karşılığı */}
      <table className="sr-only">
        <caption>Sınıf olasılıkları</caption>
        <tbody>
          {data.map((d) => (
            <tr key={d.cls}>
              <th>{d.name}</th>
              <td>{formatPercent(d.value)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </figure>
  )
}
