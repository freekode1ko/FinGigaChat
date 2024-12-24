import { Moon, Sun } from 'lucide-react'

import { selectAppTheme, setTheme } from '@/entities/theme'
import { useAppDispatch, useAppSelector } from '@/shared/lib'
import { Button } from '@/shared/ui'

interface ThemeSwitcherProps {
  hideText?: boolean
}

const ThemeSwitcher = ({ hideText }: ThemeSwitcherProps) => {
  const appTheme = useAppSelector(selectAppTheme)
  const dispatch = useAppDispatch()

  if (appTheme === 'light')
    return (
      <Button
        variant="ghost"
        size="icon"
        onClick={() => dispatch(setTheme('dark'))}
        className="px-2 py-1.5 justify-start"
      >
        <Sun /> {!hideText && 'Светлая тема'}
      </Button>
    )
  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={() => dispatch(setTheme('light'))}
      className="px-2 py-1.5 justify-start"
    >
      <Moon /> {!hideText && 'Темная тема'}
    </Button>
  )
}

export { ThemeSwitcher }
