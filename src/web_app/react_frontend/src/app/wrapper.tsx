import React, { useEffect, useState } from 'react'

import { Logo } from '@/features/logo'
import { setUser } from '@/entities/user'
import { useAppDispatch, useInitData, useWebApp } from '@/shared/lib'
import { Paragraph } from '@/shared/ui'

const InitializationWrapper = ({ children }: React.PropsWithChildren) => {
  const dispatch = useAppDispatch()
  const tg = useWebApp()
  const [userData] = useInitData()
  const [isReady, setIsReady] = useState<boolean>(false)

  useEffect(() => {
    if (tg && userData && userData.user) {
      dispatch(setUser({userId: userData.user.id}))
      tg.expand()
      tg.ready()
    } else {
      console.warn(
        'Приложение запущено не в Telegram: некоторые функции недоступны'
      )
    }
    setIsReady(true)
  }, [tg, userData])

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
