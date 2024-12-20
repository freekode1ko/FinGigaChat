import { NavLink } from 'react-router-dom'

import { cn } from '@/shared/lib'

import { type MenuItem, menuItems } from '../model'

const MenuItemLink = ({ item }: { item: MenuItem }) => (
  <NavLink
    to={item.path}
    className={({ isActive }) =>
      cn(
        isActive ? 'text-accent' : 'text-foreground hover:text-accent',
        'font-semibold'
      )
    }
  >
    <span className="flex flex-col items-center justify-center gap-1 p-2">
      <item.icon />
      <p className="text-center leading-tight">{item.name}</p>
    </span>
  </NavLink>
)

/*
  Компонент с навигационными кнопками для мобильных устройств.
  Отображается на устройствах со узким экраном.
*/
export const NavigationTabs = () => {
  return (
    <nav
      className={cn(
        'md:hidden sticky bottom-0 w-full bg-background border-t border-border z-50 items-center grid grid-cols-3 py-2'
      )}
    >
      {menuItems.map((item) => (
        <MenuItemLink key={item.path} item={item} />
      ))}
    </nav>
  )
}
