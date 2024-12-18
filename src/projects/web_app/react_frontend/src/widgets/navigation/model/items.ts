import {
  ClipboardPen,
  Factory,
  FileBarChart,
  LayoutDashboardIcon,
  ListChecks,
  LucideIcon,
  NewspaperIcon,
  NotebookPen,
  Package,
  Podcast,
  Settings,
  ShoppingCart,
  UserIcon,
} from 'lucide-react'

import { ADMIN_MAP, SITE_MAP } from '@/shared/model'

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

export const adminItems: Array<MenuItem> = [
  {
    name: 'Доступы',
    path: ADMIN_MAP.whitelist,
    icon: ClipboardPen,
    description: 'Управление белым списком',
  },
  {
    name: 'Пользователи',
    path: ADMIN_MAP.users,
    icon: UserIcon,
    description: 'Просмотр пользователей',
  },
  {
    name: 'Продукты',
    path: ADMIN_MAP.home,
    icon: ShoppingCart,
    description: 'Управление продуктами',
  },
  {
    name: 'Отрасли',
    path: ADMIN_MAP.industries,
    icon: Factory,
    description: 'Управление отраслями',
  },
  {
    name: 'Товары',
    path: ADMIN_MAP.commodities,
    icon: Package,
    description: 'Управление commodities',
  },
  {
    name: 'Настройки',
    path: ADMIN_MAP.settings,
    icon: Settings,
    description: 'Управление настройками приложения',
  },
]
