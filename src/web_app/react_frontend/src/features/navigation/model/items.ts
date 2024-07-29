import {
  ActivityIcon,
  LayoutDashboardIcon,
  type LucideIcon,
  NewspaperIcon,
} from 'lucide-react'

interface MenuItem {
  name: string
  path: string
  icon: LucideIcon
}

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
