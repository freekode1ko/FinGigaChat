import { createElement } from 'react'
import { NavLink } from 'react-router-dom'

import { cn } from '@/shared/lib'

import { menuItems } from '../model'

export const Navigation = () => {
  return (
    <nav className="flex flex-nowrap">
      {menuItems.map((item, index) => (
        <NavLink
          to={item.path}
          className={({ isActive }) =>
            cn(
              'flex flex-grow gap-2 justify-center no-underline py-4',
              isActive
                ? 'font-medium border-b-2 border-accent-text-color text-accent-text-color'
                : 'hover:text-accent-text-color'
            )
          }
          key={index}
        >
          {createElement(item.icon)}
          {item.name}
        </NavLink>
      ))}
    </nav>
  )
}
