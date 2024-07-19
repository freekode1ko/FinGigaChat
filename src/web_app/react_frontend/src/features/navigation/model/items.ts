import { ActivityIcon, LayoutDashboardIcon, NewspaperIcon } from 'lucide-react'

import type { MenuItem } from './types'

export const menuItems: Array<MenuItem> = [
  {
    name: 'Котировки',
    path: '/quotes/show',
    icon: ActivityIcon,
  },
  {
    name: 'Дашборд',
    path: '/dashboard/show',
    icon: LayoutDashboardIcon,
  },
  {
    name: 'Новости',
    path: '/news/show',
    icon: NewspaperIcon,
  },
]
