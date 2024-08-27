import { Info } from 'lucide-react'
import { Link } from 'react-router-dom'

import { selectUserIsAuthenticated } from '@/entities/user'
import { useAppSelector } from '@/shared/lib'
import { Button, Paragraph, TypographyH2 } from '@/shared/ui'

interface ProtectionWrapperInterface extends React.PropsWithChildren {
  hideElement?: boolean
  showHomeButton?: boolean
}

const ProtectedWrapper = ({ hideElement, showHomeButton, children }: ProtectionWrapperInterface) => {
  const isAuthenticated = useAppSelector(selectUserIsAuthenticated)

  if (!isAuthenticated && hideElement) return 

  if (!isAuthenticated) {
    return (
      <div className='flex flex-col gap-8'>
        <div className='flex gap-2'>
          <Info className='h-8 w-8' />
          <TypographyH2>Данный раздел недоступен</TypographyH2>
        </div>
        <div className='flex flex-col gap-4'>
          <Paragraph>Пожалуйста, используйте Telegram, чтобы получить доступ к этому разделу</Paragraph>
          {showHomeButton &&
            <Button asChild>
              <Link to='/'>На главную</Link>
            </Button>
          }
        </div>
      </div>
    )
  }

  return children
}

export { ProtectedWrapper }
