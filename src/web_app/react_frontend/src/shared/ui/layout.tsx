import React from 'react'
import { Outlet } from 'react-router-dom'

type LayoutProps = {
  headerSlot?: React.ReactNode
  bottomMenuSlot?: React.ReactNode
}

const Layout = ({ headerSlot, bottomMenuSlot }: LayoutProps) => {
  return (
    <div className="flex flex-col justify-start min-h-screen scroll-smooth bg-white text-dark-blue dark:bg-dark-blue dark:text-white">
      {headerSlot}
      <div className="flex-1 w-full px-4 max-w-3xl mx-auto xl:px-16 xl:max-w-none">
        <Outlet />
      </div>
      {bottomMenuSlot}
    </div>
  )
}

export { Layout }
