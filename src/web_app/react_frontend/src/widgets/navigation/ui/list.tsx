import { NavLink } from 'react-router-dom'

import { cn } from '@/shared/lib'

import { type MenuItem, menuItems } from '../model'


const MenuItemLink = ({ item }: { item: MenuItem }) => (
  <NavLink
    to={item.path}
    className={({ isActive }) =>
      cn(
        isActive
          ? 'text-accent'
          : 'text-foreground hover:text-accent',
          'font-semibold'
      )
    }
  >
    <span className="flex items-center justify-center gap-2 p-2">
      <item.icon />
      <p className="text-center leading-tight">{item.name}</p>
    </span>
  </NavLink>
)

/*
  Компонент с навигационными кнопками для шапки.
  Представляет из себя горизонтальный список с кнопками для перехода на разные экраны.
*/
export const NavigationList = () => {
  return (
      <nav className='flex w-full items-center py-2 gap-4'>
        {menuItems.map((item) => (
            <MenuItemLink key={item.path} item={item} />
        ))}
      </nav>
  )
}
