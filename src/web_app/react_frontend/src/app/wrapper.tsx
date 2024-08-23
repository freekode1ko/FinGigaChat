import React, { useEffect, useState } from 'react'

import { Logo } from '@/features/logo'
import { useWebApp } from '@/shared/lib'
import { Paragraph } from '@/shared/ui'

const InitializationWrapper = ({ children }: React.PropsWithChildren) => {
  const tg = useWebApp()
  const [isReady, setIsReady] = useState<boolean>(false)

  useEffect(() => {
    if (tg && tg.initData) {
      tg.expand()
      tg.ready()
    } else {
      console.log(
        'Приложение запущено не в Telegram: некоторые функции недоступны'
      )
    }
    setIsReady(true)
  }, [tg])

  if (!isReady)
    return (
      <div className="h-screen flex items-center justify-center text-dark-blue dark:text-white bg-white dark:bg-dark-blue">
        <div className="mx-auto w-full text-center transition animate-pulse">
          <Logo />
          <Paragraph>Загружаем приложение</Paragraph>
        </div>
      </div>
    )
  return <>{children}</>
}

export { InitializationWrapper }
