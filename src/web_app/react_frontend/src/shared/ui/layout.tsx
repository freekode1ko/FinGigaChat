import React from 'react'
import { Outlet } from 'react-router-dom'

type LayoutProps = {
  headerSlot?: React.ReactNode
  bottomMenuSlot?: React.ReactNode
}

const Layout = ({ headerSlot, bottomMenuSlot }: LayoutProps) => {
  return (
    <div className="flex flex-col justify-start min-h-screen scroll-smooth bg-background text-text">
      {headerSlot}
      <div className="flex-1 w-full">
        <Outlet />
      </div>
      {bottomMenuSlot}
    </div>
  )
}

export { Layout }
