import {
  ActivityIcon,
  FileBarChart,
  LayoutDashboardIcon,
  ListChecks,
  LucideIcon,
  NewspaperIcon,
  NotebookPen,
  Podcast,
} from 'lucide-react'

import { SITE_MAP } from '@/shared/model'

export interface MenuItem {
  name: string
  description: string
  path: string
  needAuth: boolean
  icon: LucideIcon
}

export const menuItems: Array<MenuItem> = [
  {
    name: 'Котировки',
    path: SITE_MAP.quotes,
    icon: ActivityIcon,
    needAuth: false,
    description: 'Отслеживайте последние рыночные котировки и данные',
  },
  {
    name: 'Дашборд',
    path: SITE_MAP.dashboard,
    icon: LayoutDashboardIcon,
    needAuth: false,
    description: 'Создайте свой персональный дашборд с ключевыми показателями',
  },
  {
    name: 'Новости',
    path: SITE_MAP.news,
    icon: NewspaperIcon,
    needAuth: false,
    description: 'Последние новости и события в мире финансов',
  },
  {
    name: 'Подписки',
    path: SITE_MAP.subscriptions,
    icon: Podcast,
    needAuth: true,
    description:
      'Настраивайте подписки, чтобы получать только актуальную информацию',
  },
  {
    name: 'Аналитика',
    path: SITE_MAP.analytics,
    icon: FileBarChart,
    needAuth: true,
    description: 'Аналитика поможет гранулярно изучить конкретные отрасли',
  },
  {
    name: 'Встречи',
    path: SITE_MAP.meetings,
    icon: ListChecks,
    needAuth: true,
    description: 'Напоминания о встречах и задачах',
  },
  {
    name: 'Заметки',
    path: SITE_MAP.notes,
    icon: NotebookPen,
    needAuth: true,
    description: 'Ведите заметки, чтобы ничего не забыть',
  },
]
