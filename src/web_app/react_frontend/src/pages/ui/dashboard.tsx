import { useEffect } from 'react'
import { Link, Outlet, useParams } from 'react-router-dom'

import { ManageDashboardButton } from '@/widgets/dashboard/management'
import { DashboardSection } from '@/widgets/dashboard-section'
import { ChartSkeleton } from '@/entities/charts'
import {
  setSubscriptions,
  useGetDashboardSubscriptionsQuery,
  useGetUserDashboardQuery,
} from '@/entities/quotes'
import { selectUserData } from '@/entities/user'
import { useAppDispatch, useAppSelector } from '@/shared/lib'
import { Button, Paragraph, TypographyH2 } from '@/shared/ui'
import { skipToken } from '@reduxjs/toolkit/query'

const DashboardPage = () => {
  const dispatch = useAppDispatch()
  const { userId } = useParams() as { userId?: string }
  const user = useAppSelector(selectUserData)
  const { data: initialContent, isLoading } = useGetUserDashboardQuery(
    userId
      ? { userId: parseInt(userId) }
      : user
        ? { userId: user.id }
        : skipToken
  )
  const { data } = useGetDashboardSubscriptionsQuery(
    user ? { userId: user.id } : skipToken
  )

  useEffect(() => {
    if (data) {
      dispatch(setSubscriptions(data.subscription_sections))
    }
  }, [data, dispatch])

  return (
    <>
      {!user && (
        <div className="pt-10 pb-4 flex justify-center">
          <Button asChild>
            <Link to='/login'>Войти</Link>
          </Button>
        </div>
      )}
      <div className="pt-10 pb-4 flex justify-between items-center gap-4 lg:justify-end lg:flex-row-reverse mb-4">
        <TypographyH2>
          Дашборд {userId && `пользователя ${userId}`}
        </TypographyH2>
        {!userId && user && <ManageDashboardButton />}
      </div>
      <div className="gap-8 pt-6 columns-1 lg:columns-2 xl:columns-3 lg:pt-0">
        <>
          {isLoading &&
            Array.from({ length: 20 }).map((_, idx) => (
              <div className="h-[300px] mb-2" key={idx}>
                <ChartSkeleton />
              </div>
            ))}
          {initialContent?.sections.length == 0 && (
            <Paragraph>Данный дашборд пуст или не существует.</Paragraph>
          )}
          {initialContent?.sections.map((section) => (
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
