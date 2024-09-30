import { MoreHorizontal } from 'lucide-react'
import { useState } from 'react'
import { matchPath, NavLink, useLocation } from 'react-router-dom'

import { selectUserIsAuthenticated } from '@/entities/user'
import { cn, useAppSelector } from '@/shared/lib'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/shared/ui'

import { type MenuItem, menuItems } from '../model'

const MenuItemLink = ({ item }: { item: MenuItem }) => (
  <NavLink
    to={item.path}
    className={({ isActive }) =>
      cn(
        isActive
          ? 'text-dark-blue dark:text-white'
          : 'text-secondary-300 dark:text-secondary-600'
      )
    }
  >
    <span className="flex flex-col items-center justify-center p-2">
      <item.icon />
      {item.name}
    </span>
  </NavLink>
)

const MoreMenuButton = ({ overflowTabs }: { overflowTabs: MenuItem[] }) => {
  const location = useLocation()
  const [isOpen, setIsOpen] = useState(false)

  const isTabActive = overflowTabs.some((tab) =>
    matchPath({ path: tab.path, end: false }, location.pathname)
  )
  return (
    <DropdownMenu open={isOpen} onOpenChange={setIsOpen}>
      <DropdownMenuTrigger asChild>
        <button
          className={cn(
            'flex flex-col items-center justify-center p-2',
            isTabActive
              ? 'text-dark-blue dark:text-white'
              : 'text-secondary-300 dark:text-secondary-600'
          )}
        >
          <span className="flex flex-col items-center justify-center p-2">
            <MoreHorizontal />
            Еще
          </span>
        </button>
      </DropdownMenuTrigger>
      <DropdownMenuContent className="w-56">
        {overflowTabs.map((item) => (
          <DropdownMenuItem key={item.path}>
            <NavLink
              to={item.path}
              className={({ isActive }) =>
                cn(
                  'w-full py-2',
                  isActive
                    ? 'text-dark-blue dark:text-white'
                    : 'text-secondary-300 dark:text-secondary-600'
                )
              }
              onClick={() => setIsOpen(false)}
            >
              <span className="flex items-center">
                <item.icon className="mr-2" />
                {item.name}
              </span>
            </NavLink>
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  )
}

export const NavigationTabs = () => {
  const isAuthenticated = useAppSelector(selectUserIsAuthenticated)
  const filteredMenuItems = menuItems.filter(
    (item) => !item.needAuth || isAuthenticated
  )
  const visibleTabs = filteredMenuItems.slice(0, 3)
  const overflowTabs = filteredMenuItems.slice(3)
  return (
    <nav
      className={cn(
        'fixed bottom-0 w-full dark:bg-dark-blue bg-white z-40 items-center grid',
        overflowTabs.length > 0 ? 'grid-cols-4' : 'grid-cols-3'
      )}
    >
      {visibleTabs.map((item) => (
        <MenuItemLink key={item.path} item={item} />
      ))}
      {overflowTabs.length > 0 && (
        <MoreMenuButton overflowTabs={overflowTabs} />
      )}
    </nav>
  )
}
