/**
 * Arayüzde gösterilen kategori bilgileri (simge, açıklama, örnekler).
 *
 * NOT: Geri dönüşüm kutusu renkleri burada DEĞİL, backend'deki
 * app/data/recycling_config.json dosyasındadır; çünkü belediyeye göre değişir.
 * Buradaki "accent" renkleri yalnızca arayüz süslemesidir.
 */

import { Cylinder, Milk, Newspaper, Wine, type LucideIcon } from 'lucide-react'
import type { ModelClass, WasteClass } from '../types/api'

export interface CategoryMeta {
  id: WasteClass
  nameTr: string
  nameEn: string
  icon: LucideIcon
  description: string
  examples: string[]
  /** Tailwind sınıfları: simge arka planı ve rengi */
  accent: string
}

export const CATEGORIES: CategoryMeta[] = [
  {
    id: 'plastic',
    nameTr: 'Plastik',
    nameEn: 'Plastic',
    icon: Milk,
    description: 'Pet şişeler, plastik ambalajlar ve kaplar.',
    examples: ['Pet şişe', 'Deterjan kutusu', 'Plastik kap'],
    accent: 'bg-amber-100 text-amber-700 dark:bg-amber-500/15 dark:text-amber-300',
  },
  {
    id: 'paper',
    nameTr: 'Kâğıt',
    nameEn: 'Paper',
    icon: Newspaper,
    description: 'Gazete, dergi, defter ve karton kutular.',
    examples: ['Gazete', 'Karton kutu', 'Ofis kâğıdı'],
    accent: 'bg-sky-100 text-sky-700 dark:bg-sky-500/15 dark:text-sky-300',
  },
  {
    id: 'metal',
    nameTr: 'Metal',
    nameEn: 'Metal',
    icon: Cylinder,
    description: 'İçecek kutuları, konserve ve metal kapaklar.',
    examples: ['Kola kutusu', 'Konserve', 'Alüminyum folyo'],
    accent: 'bg-slate-200 text-slate-700 dark:bg-slate-500/20 dark:text-slate-300',
  },
  {
    id: 'glass',
    nameTr: 'Cam',
    nameEn: 'Glass',
    icon: Wine,
    description: 'Cam şişeler ve kavanozlar.',
    examples: ['Cam şişe', 'Reçel kavanozu', 'Cam bardak*'],
    accent: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-500/15 dark:text-emerald-300',
  },
]

/** Grafiklerde ve listelerde kullanılan Türkçe adlar ("other" dahil) */
export const CLASS_LABEL_TR: Record<ModelClass, string> = {
  plastic: 'Plastik',
  paper: 'Kâğıt',
  metal: 'Metal',
  glass: 'Cam',
  other: 'Diğer',
}

/** Grafiklerde sabit sınıf sırası */
export const CLASS_ORDER: ModelClass[] = ['plastic', 'paper', 'metal', 'glass', 'other']
