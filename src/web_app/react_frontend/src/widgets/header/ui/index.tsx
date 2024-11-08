import { NavigationList } from '@/widgets/navigation'
import { Logo } from '@/features/logo'
import { ThemeSwitcher } from '@/features/theme-switcher'

/*
  Компонент шапки веб-страницы.
  Отображается на устройствах со средним экраном и шире.
*/
export const Header = () => {
  return (
    <header className="hidden sticky top-0 w-full border-b border-border md:flex justify-between items-center bg-background backdrop-blur supports-[backdrop-filter]:bg-background/60 z-50 px-4 h-16">
      <Logo navigateOnClick />
      <div>
        <NavigationList />
      </div>
      <ThemeSwitcher hideText />
    </header>
  )
}
