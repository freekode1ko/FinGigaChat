import {
  FileBarChart,
  LayoutDashboardIcon,
  ListChecks,
  LucideIcon,
  NewspaperIcon,
  NotebookPen,
  Podcast,
  UserIcon,
} from 'lucide-react'

import { SITE_MAP } from '@/shared/model'

export interface MenuItem {
  name: string
  description: string
  path: string
  icon: LucideIcon
}

export const menuItems: Array<MenuItem> = [
  {
    name: 'BRIEF Terminal',
    path: SITE_MAP.dashboard,
    icon: LayoutDashboardIcon,
    description: 'Создайте свой персональный дашборд с ключевыми показателями',
  },
  {
    name: 'Новости',
    path: SITE_MAP.news,
    icon: NewspaperIcon,
    description: 'Последние новости и события в мире финансов',
  },
  {
    name: 'Профиль',
    path: SITE_MAP.profile,
    icon: UserIcon,
    description: 'Последние новости и события в мире финансов',
  },
]

export const profileItems: Array<MenuItem> = [
  {
    name: 'Аналитика',
    path: SITE_MAP.analytics,
    icon: FileBarChart,
    description: 'Аналитика поможет гранулярно изучить конкретные отрасли',
  },
  {
    name: 'Подписки',
    path: SITE_MAP.subscriptions,
    icon: Podcast,
    description:
      'Настраивайте подписки, чтобы получать только актуальную информацию',
  },
  {
    name: 'Встречи',
    path: SITE_MAP.meetings,
    icon: ListChecks,
    description: 'Напоминания о встречах и задачах',
  },
  {
    name: 'Заметки',
    path: SITE_MAP.notes,
    icon: NotebookPen,
    description: 'Ведите заметки, чтобы ничего не забыть',
  },
]
