import React from 'react'

import { Logo } from '@/features/logo'
import { useInitializeUser } from '@/entities/user'
import { AutoProgress } from '@/shared/kit'

const InitializationWrapper = ({ children }: React.PropsWithChildren) => {
  const isInitializing = useInitializeUser()
  if (isInitializing)
    return (
      <div className="h-screen w-full flex items-center justify-center text-text bg-background">
        <div className="mx-auto w-full text-center md:max-w-xs px-8 space-y-4">
          <Logo />
          <AutoProgress />
        </div>
      </div>
    )
  return children
}

export { InitializationWrapper }
