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

import { adminItems, menuItems } from '../model'

export const NavigationSheet = ({
  content,
}: {
  content: 'common' | 'admin'
}) => {
  const [isOpen, setIsOpen] = useState<boolean>(false)
  const items = content === 'common' ? menuItems : adminItems

  return (
    <Sheet open={isOpen} onOpenChange={setIsOpen}>
      <Button variant="ghost" size="icon" onClick={() => setIsOpen(true)}>
        <LayoutGrid className="h-6 w-6" />
      </Button>
      <SheetContent side="left">
        <SheetHeader>
          <SheetTitle>Навигация</SheetTitle>
        </SheetHeader>
        <div className="min-w-full table">
          <div className="flex flex-col space-y-3 mt-8">
            {items.map((item, itemIdx) => (
              <NavLink
                end
                key={itemIdx}
                to={item.path}
                className={({ isActive }) =>
                  cn(
                    'flex gap-2 no-underline py-2',
                    isActive
                      ? 'font-semibold border-l-2 border-accent text-accent'
                      : 'hover:text-accent'
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
