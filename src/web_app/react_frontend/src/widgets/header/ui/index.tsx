import { Logo } from '@/features/logo'
import { ThemeSwitcher } from '@/features/theme-switcher'

export const Header = () => {
  return (
    <header className="sticky top-0 w-full flex flex-row-reverse justify-between items-center shadow-md shadow-black/5 dark:bg-dark-blue bg-white backdrop-blur supports-[backdrop-filter]:bg-white/60 dark:supports-[backdrop-filter]:bg-dark-blue/60 z-40 py-2 px-4 gap-4">
      <div className="absolute left-1/2 transform -translate-x-1/2">
        <Logo navigateOnClick />
      </div>
      <ThemeSwitcher />
    </header>
  )
}
