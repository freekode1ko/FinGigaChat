import { type ReactNode } from 'react'
import { Outlet } from 'react-router-dom'

type Props = {
  headerSlot?: ReactNode
}

const Layout = ({ headerSlot }: Props) => {
  return (
    <div className="min-h-screen scroll-smooth bg-white text-dark-blue dark:bg-dark-blue dark:text-white">
      {headerSlot}
      <div className="flex flex-col gap-4 p-4 lg:max-w-screen-lg lg:m-auto">
        <Outlet />
      </div>
    </div>
  )
}

export { Layout }
