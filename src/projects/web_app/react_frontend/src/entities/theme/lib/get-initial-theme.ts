import { getWebAppFromGlobal } from '@/shared/lib'

const getInitialTheme = (): Theme => {
  const tg = getWebAppFromGlobal()
  if (tg && tg.initData) {
    return tg.colorScheme
  } else {
    return window.matchMedia('(prefers-color-scheme: dark)').matches
      ? 'dark'
      : 'light'
  }
}

export { getInitialTheme }
