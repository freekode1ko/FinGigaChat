import {
  ActivityIcon,
  FileBarChart,
  LayoutDashboardIcon,
  ListChecks,
  type LucideIcon,
  NewspaperIcon,
  NotebookPen,
  Podcast,
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
  {
    name: 'Подписки',
    path: '/subscriptions',
    icon: Podcast,
  },
  {
    name: 'Аналитика',
    path: '/analytics',
    icon: FileBarChart,
  },
  {
    name: 'Встречи',
    path: '/meetings',
    icon: ListChecks,
  },
  {
    name: 'Заметки',
    path: '/notes',
    icon: NotebookPen,
  },
]
