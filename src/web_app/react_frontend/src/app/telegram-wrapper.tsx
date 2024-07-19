import React, { useEffect } from 'react'

import { applyTelegramTheme } from '@/shared/lib'

export const TelegramWrapper = ({ children }: React.PropsWithChildren) => {
  useEffect(() => {
    if (window.Telegram && window.Telegram.WebApp) {
      const tg = window.Telegram.WebApp
      if (tg.themeParams) {
        applyTelegramTheme(tg.themeParams)
      }
      tg.ready()
    } else {
      console.warn('Telegram WebApp недоступен')
    }
  }, [])

  return <>{children}</>
}
