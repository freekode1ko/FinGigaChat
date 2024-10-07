import { Outlet } from 'react-router-dom'

import { DashboardSection } from '@/widgets/dashboard-section'
import { ManageDashboardButton } from '@/features/manage-dashboard'
import { TelegramAuthButton } from '@/features/user'
import { ChartSkeleton } from '@/entities/charts'
import { useGetDashboardSubscriptionsQuery } from '@/entities/quotes'
import { selectUserData } from '@/entities/user'
import { useAppSelector } from '@/shared/lib'
import { TypographyH2 } from '@/shared/ui'
import { skipToken } from '@reduxjs/toolkit/query'

const DashboardPage = () => {
  const user = useAppSelector(selectUserData)
  const { data: initialContent, isLoading } = useGetDashboardSubscriptionsQuery(
    user
      ? {
          userId: user.userId,
        }
      : skipToken
  )

  if (!user) {
    return (
      <div className='pt-4 lg:pt-10 flex justify-center'><TelegramAuthButton /></div>
    )
  }

  return (
    <>
      <div className="flex justify-between items-center gap-4 lg:justify-end lg:flex-row-reverse mb-4">
        <TypographyH2>Дашборд</TypographyH2>
        <ManageDashboardButton />
      </div>
      <div className="gap-8 pt-6 columns-1 lg:columns-2 xl:columns-3 lg:pt-0">
        <>
          {isLoading &&
            Array.from({ length: 20 }).map((_, idx) => (
              <div className="h-[300px]" key={idx}>
                <ChartSkeleton />
              </div>
            ))}
          {initialContent?.subscription_sections.map((section) => (
            <DashboardSection key={section.section_name} section={section} />
          ))}
        </>
      </div>
      {/* Opens detailed drawer (dashboard quotation page) */}
      <Outlet />
    </>
  )
}

export { DashboardPage }
