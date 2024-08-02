import { LayoutGrid } from 'lucide-react'
import { createElement, useState } from 'react'
import { NavLink } from 'react-router-dom'

import { cn } from '@/shared/lib'
import {
  Button,
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from '@/shared/ui'

import { menuItems } from '../model'

export const Navigation = () => {
  const [isOpen, setIsOpen] = useState<boolean>(false)

  return (
    <Sheet open={isOpen} onOpenChange={setIsOpen}>
      <Button
        variant="outline"
        size="icon"
        className="border-none"
        onClick={() => setIsOpen(true)}
      >
        <LayoutGrid className="h-6 w-6" />
      </Button>
      <SheetContent side="left">
        <SheetHeader>
          <SheetTitle>Навигация</SheetTitle>
        </SheetHeader>
        <div className="min-w-full table">
          <div className="flex flex-col space-y-3 mt-8">
            {menuItems.map((item, itemIdx) => (
              <NavLink
                key={itemIdx}
                to={item.path}
                className={({ isActive }) =>
                  cn(
                    'flex gap-2 no-underline py-2',
                    isActive
                      ? 'font-medium border-b-2 border-primary-800 text-primary-800 dark:border-primary-300 dark:text-primary-300'
                      : 'text-dark-blue hover:text-primary-800 dark:text-white dark:hover:text-primary-300'
                  )
                }
                onClick={() => setIsOpen(false)}
              >
                <span className="inline-flex items-center gap-2">
                  {createElement(item.icon, { className: 'h-4 w-4' })}
                  {item.name}
                </span>
              </NavLink>
            ))}
          </div>
        </div>
      </SheetContent>
    </Sheet>
  )
}
