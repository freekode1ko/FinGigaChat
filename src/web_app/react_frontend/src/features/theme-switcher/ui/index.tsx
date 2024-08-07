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
        variant="outline"
        size="icon"
        onClick={() => dispatch(setTheme('dark'))}
        className="border-none"
      >
        <Sun />
      </Button>
    )
  return (
    <Button
      variant="outline"
      size="icon"
      onClick={() => dispatch(setTheme('light'))}
      className="border-none"
    >
      <Moon />
    </Button>
  )
}

export { ThemeSwitcher }
