import React, { useEffect } from 'react'

import { applyTheme, useWebApp } from '@/shared/lib'

export const TelegramWrapper = ({ children }: React.PropsWithChildren) => {
  const tg = useWebApp()

  useEffect(() => {
    if (tg && tg.initData) {
      applyTheme(tg.colorScheme)
      tg.expand()
      tg.ready()
    } else {
      if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
        applyTheme('dark')
      } else {
        applyTheme('light')
      }
      console.log(
        'Приложение запущено не в Telegram: некоторые функции недоступны'
      )
    }
  }, [tg])

  return <>{children}</>
}
