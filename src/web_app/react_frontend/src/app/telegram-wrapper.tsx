import React, { useEffect } from 'react'

import { applyTelegramTheme, useWebApp } from '@/shared/lib'

export const TelegramWrapper = ({ children }: React.PropsWithChildren) => {
  const tg = useWebApp()

  useEffect(() => {
    if (tg) {
      applyTelegramTheme(tg.themeParams)
      tg.expand()
      tg.ready()
    } else {
      console.warn(
        'Приложение открыто не в Telegram: некоторые функции недоступны'
      )
    }
  }, [tg])

  return <>{children}</>
}
