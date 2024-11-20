import { ProfileNavigation } from "@/widgets/navigation"
import { selectUserData } from "@/entities/user"
import { getCurrentGreeting, useAppSelector } from "@/shared/lib"
import { TypographyH2 } from "@/shared/ui"

const ProfilePage = () => {
  const user = useAppSelector(selectUserData)
  return (
    <div className="flex flex-col gap-10 mx-auto px-4 lg:max-w-screen-sm pt-5 pb-2">
      <TypographyH2>{getCurrentGreeting()}, {user?.email}!</TypographyH2>
      <ProfileNavigation />
    </div>
  )
}

export { ProfilePage }
