import { type ReactNode } from 'react'
import { Outlet } from 'react-router-dom'

type Props = {
  headerSlot?: ReactNode
}

const Layout = ({ headerSlot }: Props) => {
  return (
    <div className="min-h-screen scroll-smooth bg-white text-dark-blue dark:bg-dark-blue dark:text-white">
      {headerSlot}
      <div className="p-4 max-w-3xl mx-auto pt-10 xl:p-16 xl:max-w-none">
        <Outlet />
      </div>
    </div>
  )
}

export { Layout }
