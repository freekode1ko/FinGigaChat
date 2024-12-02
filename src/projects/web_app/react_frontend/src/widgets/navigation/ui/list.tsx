import { NavLink } from 'react-router-dom'

import { cn } from '@/shared/lib'

import { adminItems, type MenuItem, menuItems } from '../model'

const MenuItemLink = ({ item }: { item: MenuItem }) => (
  <NavLink
    end
    to={item.path}
    className={({ isActive }) =>
      cn(
        isActive ? 'text-accent' : 'text-foreground hover:text-accent',
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
export const NavigationList = ({
  dir = 'horizontal',
  content = 'common',
}: {
  dir?: 'horizontal' | 'vertical'
  content?: 'common' | 'admin'
}) => {
  return (
    <nav
      className={cn(
        'flex items-center py-2 gap-4',
        dir === 'vertical' && 'flex-col'
      )}
    >
      {content === 'common'
        ? menuItems.map((item) => <MenuItemLink key={item.path} item={item} />)
        : adminItems.map((item) => (
            <MenuItemLink key={item.path} item={item} />
          ))}
    </nav>
  )
}
