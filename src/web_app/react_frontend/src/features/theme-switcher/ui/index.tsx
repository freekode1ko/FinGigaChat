import { Moon, Sun } from 'lucide-react'

import { selectAppTheme, setTheme } from '@/entities/theme'
import { useAppDispatch, useAppSelector } from '@/shared/lib'
import { Button } from '@/shared/ui'

const ThemeSwitcher = () => {
  const appTheme = useAppSelector(selectAppTheme)
  const dispatch = useAppDispatch()

  if (appTheme === 'light')
    return (
      <Button
        variant="ghost"
        size="icon"
        onClick={() => dispatch(setTheme('dark'))}
        className='w-full px-2 py-1.5 justify-start'
      >
        <Sun /> Светлая тема
      </Button>
    )
  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={() => dispatch(setTheme('light'))}
      className='w-full px-2 py-1.5 justify-start'
    >
      <Moon /> Темная тема
    </Button>
  )
}

export { ThemeSwitcher }
