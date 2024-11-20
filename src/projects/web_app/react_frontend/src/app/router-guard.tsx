import { ChevronLeft, Construction } from 'lucide-react'
import { Navigate, useNavigate } from 'react-router-dom'

import { selectUserIsAuthenticated } from '@/entities/user'
import { useAppSelector } from '@/shared/lib'
import { SITE_MAP } from '@/shared/model'
import { Button, Paragraph, TypographyH2 } from '@/shared/ui'

interface ProtectionWrapperInterface extends React.PropsWithChildren {
  redirectHome?: boolean
}

const AuthGuard = ({
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

const DevelopGuard = () => {
  const navigate = useNavigate();
  const isFirstPage = window.history.length < 2
  const handleBackClick = () => {
    if (isFirstPage) navigate(SITE_MAP.news)
    else navigate(SITE_MAP.news)
  }

  return (
    <div className='space-y-2 lg:max-w-screen-sm pt-5 mx-auto pb-2 px-2 text-center'>
      <Construction className='h-10 w-10 mx-auto' />
      <TypographyH2>Этот раздел пока в разработке</TypographyH2>
      <Paragraph className='text-muted-foreground pb-5'>Пожалуйста, вернитесь позже или воспользуйтесь этим функционалом в боте</Paragraph>
      <Button variant='outline' size='sm' onClick={handleBackClick}>
        <ChevronLeft />
        <span>{isFirstPage ? 'Перейти на главную' : 'Перейти на главную'}</span>
      </Button>
    </div>
  )
}

export { AuthGuard, DevelopGuard }
