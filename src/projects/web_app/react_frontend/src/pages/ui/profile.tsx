import { Link } from 'react-router-dom'

import { ProfileNavigation } from '@/widgets/navigation'
import { selectUserData } from '@/entities/user'
import { getCurrentGreeting, useAppSelector } from '@/shared/lib'
import { ADMIN_MAP } from '@/shared/model'
import { Button, TypographyH2 } from '@/shared/ui'

const ProfilePage = () => {
  const user = useAppSelector(selectUserData)
  return (
    <div className="flex flex-col gap-10 mx-auto px-4 lg:max-w-screen-sm pt-5 pb-2">
      <div className="space-y-2">
        <TypographyH2>
          {getCurrentGreeting()}, {user?.full_name || user?.email}!
        </TypographyH2>
        {user?.role === 1 && (
          <Button size="sm" variant="secondary" asChild>
            <Link to={ADMIN_MAP.home}>Панель управления</Link>
          </Button>
        )}
      </div>
      <ProfileNavigation />
    </div>
  )
}

export { ProfilePage }
