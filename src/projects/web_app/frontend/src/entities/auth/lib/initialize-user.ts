import Cookies from 'js-cookie'
import { useEffect, useState } from 'react'

import { useAppDispatch, useInitData, useWebApp } from '@/shared/lib'

import {
  useLazyGetCurrentUserQuery,
  useValidateTelegramDataMutation,
} from '../api'

/*
  Кастомный хук для получения текущего пользователя.
  Должен вызываться при инициализации приложения.
*/
export const useInitializeUser = () => {
  const dispatch = useAppDispatch()
  const [getUser] = useLazyGetCurrentUserQuery()
  const [validateTelegram] = useValidateTelegramDataMutation()
  const [isInitializing, setIsInitializing] = useState(true)

  const auth = Cookies.get('auth')
  const tg = useWebApp()
  const [initData, initDataString] = useInitData()

  useEffect(() => {
    const initializeUser = async () => {
      try {
        if (auth) {
          await getUser().unwrap()
        } else if (tg && initData && initData.user) {
          tg.expand()
          tg.ready()
          await validateTelegram({
            id: initData.user.id,
            data: initDataString || '',
          }).unwrap()
          await getUser().unwrap()
        }
      } catch {
        console.log('Ошибка авторизации')
      } finally {
        setIsInitializing(false)
      }
    }

    initializeUser()
  }, [auth, tg, initData, initDataString, getUser, validateTelegram, dispatch])

  return isInitializing
}
