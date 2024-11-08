import { Navigate } from 'react-router-dom'

import { selectUserIsAuthenticated } from '@/entities/user'
import { useAppSelector } from '@/shared/lib'
import { SITE_MAP } from '@/shared/model'

interface ProtectionWrapperInterface extends React.PropsWithChildren {
  redirectHome?: boolean
}

const ProtectedWrapper = ({
  redirectHome,
  children,
}: ProtectionWrapperInterface) => {
  const isAuthenticated = useAppSelector(selectUserIsAuthenticated)

  if (!isAuthenticated && redirectHome) {
    return <Navigate to={SITE_MAP.news} />
  }
  if (!isAuthenticated) {
    return <Navigate to={SITE_MAP.login} />
  }
  return children
}

export { ProtectedWrapper }
