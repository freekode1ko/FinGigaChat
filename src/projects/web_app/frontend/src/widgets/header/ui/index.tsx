import React from 'react'
import { Link } from 'react-router-dom'

import { NavigationList } from '@/widgets/navigation'
import { Logo } from '@/features/logo'
import { ThemeSwitcher } from '@/features/theme-switcher'
import { ADMIN_MAP } from '@/shared/model'
import { TypographyH2 } from '@/shared/ui'

/*
  Компонент шапки веб-страницы.
  Отображается на устройствах со средним экраном и шире.
*/
export const Header = () => {
  return (
    <header className="hidden w-full border-b border-border md:flex justify-between items-center bg-background px-4 h-16">
      <Logo navigateOnClick />
      <div>
        <NavigationList />
      </div>
      <ThemeSwitcher hideText />
    </header>
  )
}

/*
  Компонент шапки в админке.
  Отображается на устройствах с любым экраном.
*/
export const AdminHeader = ({
  navigationSlot,
}: {
  navigationSlot: React.ReactNode
}) => {
  return (
    <header className="w-full border-b border-border flex justify-between items-center bg-background px-4 h-16">
      <div className="inline-flex items-center gap-4">
        <div className="md:hidden">{navigationSlot}</div>
        <Link to={ADMIN_MAP.home}>
          <TypographyH2 className="uppercase">Brief Admin</TypographyH2>
        </Link>
      </div>
      <ThemeSwitcher hideText />
    </header>
  )
}
