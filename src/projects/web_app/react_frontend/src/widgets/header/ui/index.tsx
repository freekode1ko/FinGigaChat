import { NavigationList } from '@/widgets/navigation'
import { Logo } from '@/features/logo'
import { ThemeSwitcher } from '@/features/theme-switcher'

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
