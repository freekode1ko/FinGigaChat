import React, { useEffect, useState } from 'react'

import { useWebApp } from '@/shared/lib'

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

  if (!isReady) return <div>Loading...</div>
  return <>{children}</>
}

export { InitializationWrapper }
