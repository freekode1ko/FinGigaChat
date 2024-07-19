import { ActivityIcon, LayoutDashboardIcon, NewspaperIcon } from 'lucide-react'

import type { MenuItem } from './types'

export const menuItems: Array<MenuItem> = [
  {
    name: 'Котировки',
    path: '/quotes',
    icon: ActivityIcon,
  },
  {
    name: 'Дашборд',
    path: '/',
    icon: LayoutDashboardIcon,
  },
  {
    name: 'Новости',
    path: '/news',
    icon: NewspaperIcon,
  },
]
