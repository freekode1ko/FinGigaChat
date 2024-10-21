import React, { useEffect, useState } from 'react'

import { Logo } from '@/features/logo'
import { selectUserData, setUser } from '@/entities/user'
import {
  useAppDispatch,
  useAppSelector,
  useInitData,
  useWebApp,
} from '@/shared/lib'
import { Paragraph } from '@/shared/ui'

const InitializationWrapper = ({ children }: React.PropsWithChildren) => {
  const dispatch = useAppDispatch()
  const user = useAppSelector(selectUserData)
  const tg = useWebApp()
  const [initData] = useInitData()
  const [isReady, setIsReady] = useState<boolean>(false)

  useEffect(() => {
    if (!user && tg && initData && initData.user) {
      dispatch(
        setUser({
          id: initData.user.id,
          first_name: initData.user.first_name,
          last_name: initData.user.last_name,
          auth_date: initData.auth_date,
          hash: initData.hash,
        })
      )
      tg.expand()
      tg.ready()
    } else {
      console.warn(
        'Приложение запущено не в Telegram: некоторые функции недоступны'
      )
    }
    setIsReady(true)
  }, [tg, initData, dispatch, user])

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
