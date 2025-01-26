import React from 'react'
import { Outlet } from 'react-router-dom'

type LayoutProps = {
  headerSlot?: React.ReactNode
  bottomMenuSlot?: React.ReactNode
  sidebarSlot?: React.ReactNode
  adminButtonSlot?: React.ReactNode
}

const Layout = ({ headerSlot, bottomMenuSlot, sidebarSlot, adminButtonSlot }: LayoutProps) => {
  return (
    <div className="flex flex-col min-h-screen scroll-smooth bg-background text-text">
      {headerSlot}
      <div className="flex flex-1">
        {sidebarSlot && (
          <aside className="hidden md:flex w-64 bg-secondary border-r border-border">
            {sidebarSlot}
          </aside>
        )}
        <main className="flex-1 w-full">
          {adminButtonSlot}
          <Outlet />
        </main>
      </div>
      {bottomMenuSlot}
    </div>
  )
}

export { Layout }
