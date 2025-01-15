import { ChevronLeft, Construction } from 'lucide-react'
import { Navigate, useNavigate } from 'react-router-dom'

import { selectUserData } from '@/entities/auth'
import { useAppSelector } from '@/shared/lib'
import { SITE_MAP } from '@/shared/model'
import { Button, Paragraph, TypographyH2 } from '@/shared/ui'

interface ProtectionWrapperInterface extends React.PropsWithChildren {
  redirectHome?: boolean
  admin?: boolean
}

const AuthGuard = ({
  redirectHome,
  admin,
  children,
}: ProtectionWrapperInterface) => {
  const user = useAppSelector(selectUserData)

  if (!user && redirectHome) {
    return <Navigate to={SITE_MAP.news} />
  }
  if (!user) {
    return <Navigate to={SITE_MAP.login} />
  }
  if (admin && user.role !== 1) {
    // логировать, кто стучался в админку без прав
    return <Navigate to={SITE_MAP.news} />
  }
  return children
}

const DevelopGuard = () => {
  const navigate = useNavigate()
  const isFirstPage = window.history.length < 2
  const handleBackClick = () => {
    if (isFirstPage) navigate(SITE_MAP.news)
    else navigate(SITE_MAP.news)
  }

  return (
    <div className="space-y-2 lg:max-w-screen-sm pt-5 mx-auto pb-2 px-2 text-center">
      <Construction className="h-10 w-10 mx-auto" />
      <TypographyH2>Этот раздел пока в разработке</TypographyH2>
      <Paragraph className="text-muted-foreground pb-5">
        Пожалуйста, вернитесь позже или воспользуйтесь этим функционалом в боте
      </Paragraph>
      <Button variant="outline" size="sm" onClick={handleBackClick}>
        <ChevronLeft />
        <span>{isFirstPage ? 'Перейти на главную' : 'Перейти на главную'}</span>
      </Button>
    </div>
  )
}

export { AuthGuard, DevelopGuard }
