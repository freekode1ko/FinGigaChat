import { type ReactNode } from 'react'
import { Outlet } from 'react-router-dom'

type Props = {
  headerSlot?: ReactNode
}

const Layout = ({ headerSlot }: Props) => {
  return (
    <div className="bg-bg-color text-text-color min-h-screen scroll-smooth">
      {headerSlot}
      <div className="flex flex-col flex-grow gap-4 p-4 lg:max-w-screen-lg lg:m-auto">
        <Outlet />
      </div>
    </div>
  )
}

export { Layout }
