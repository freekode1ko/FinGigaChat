import React from 'react'

import { Logo } from '@/features/logo'
import { useInitializeUser } from '@/entities/user'
import { Loading } from '@/shared/kit'

const InitializationWrapper = ({ children }: React.PropsWithChildren) => {
  const isInitializing = useInitializeUser()
  if (isInitializing) return <Loading type="page" message={<Logo />} />
  return children
}

export { InitializationWrapper }
