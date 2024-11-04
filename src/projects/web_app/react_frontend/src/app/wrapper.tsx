import Cookies from 'js-cookie'
import React, { useEffect } from 'react'

import { Logo } from '@/features/logo'
import { setUser, unsetUser, useLazyGetCurrentUserQuery, useValidateTelegramDataMutation } from '@/entities/user'
import {
  useAppDispatch,
  useInitData,
  useWebApp,
} from '@/shared/lib'
import { Paragraph } from '@/shared/ui'

const InitializationWrapper = ({ children }: React.PropsWithChildren) => {
  const dispatch = useAppDispatch()
  const [getUser, {isLoading: userLoading}] = useLazyGetCurrentUserQuery()
  const [validateTelegram, {isLoading: userValidating}] = useValidateTelegramDataMutation()
  const auth = Cookies.get('auth')
  const tg = useWebApp()
  const [initData, initDataString] = useInitData()

  useEffect(() => {
    if (auth) {
      getUser().unwrap()
      .then(user => {
        dispatch(setUser(user))
      })
      .catch(() => {
        dispatch(unsetUser())
      })
    } else if (tg && initData && initData.user) {
      tg.expand()
      tg.ready()
      validateTelegram({
        hash: initData.hash,
        auth_date: initData.auth_date,
        id: initData.user!.id,
        data: initDataString || '',
      })
      .unwrap()
      .then(() => {
        dispatch(setUser({ id: initData.user!.id }))
      })
      .catch(() => {
        dispatch(unsetUser())
      })
    }

  }, [auth, tg, initData, initDataString, getUser, validateTelegram, dispatch])

  if (userLoading || userValidating)
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
