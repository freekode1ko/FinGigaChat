import { useEffect, useRef } from "react"

import { selectUserData, setUser } from "@/entities/user"
import { useAppDispatch, useAppSelector } from "@/shared/lib"

const TelegramAuthButton = () => {
  const dispatch = useAppDispatch()
  const user = useAppSelector(selectUserData)
  const tgLoginRef = useRef<HTMLDivElement>(null)
  useEffect(() => {
    if (user) return
    const button = document.createElement('script')
    button.async = true
    button.src = 'https://telegram.org/js/telegram-widget.js?22'
    button.setAttribute('data-telegram-login', 'test_fgc1_bot')
    button.setAttribute('data-size', 'medium')
    button.setAttribute('data-radius', '20')
    button.setAttribute('data-userpic', 'false')
    button.setAttribute('data-onauth', 'onTelegramAuth(user)')

    if (tgLoginRef.current) {
      tgLoginRef.current.innerHTML = ''
      tgLoginRef.current.appendChild(button)
    }

    window.onTelegramAuth = function(user: TelegramWebApps.WebAppUser) {
      dispatch(
        setUser({ userId: user.id, name: user.first_name })
      )
    }

    return () => {
      if (tgLoginRef.current) {
        tgLoginRef.current.innerHTML = ''
        delete window.onTelegramAuth
      }
    }
  }, [dispatch, user])

  if (user) return null
  return <div ref={tgLoginRef} />
}

export { TelegramAuthButton }
