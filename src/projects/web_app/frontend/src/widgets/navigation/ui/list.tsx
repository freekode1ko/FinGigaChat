import { NavLink } from 'react-router-dom'

import { cn } from '@/shared/lib'

import { adminItems, type MenuItem, menuItems } from '../model'

const MenuItemLink = ({
  item,
  dir,
}: {
  item: MenuItem
  dir: 'horizontal' | 'vertical'
}) => (
  <NavLink
    end
    to={item.path}
    className={({ isActive }) =>
      cn(
        isActive ? 'text-accent' : 'text-foreground hover:text-accent',
        'font-semibold',
        dir === 'vertical' && 'w-full'
      )
    }
  >
    <span
      className={cn(
        'flex items-center gap-2 p-2',
        dir === 'horizontal' ? 'justify-center' : 'justify-start'
      )}
    >
      <item.icon />
      <span
        className={cn(
          dir === 'vertical' ? 'leading-none' : 'text-center leading-tight'
        )}
      >
        {item.name}
      </span>
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
        ? menuItems.map((item) => (
            <MenuItemLink key={item.path} item={item} dir={dir} />
          ))
        : adminItems.map((item) => (
            <MenuItemLink key={item.path} item={item} dir={dir} />
          ))}
    </nav>
  )
}
