import { CircleHelp, CircleX } from 'lucide-react'
import { useEffect } from 'react'
import { Outlet, useParams } from 'react-router-dom'

import { ManageDashboardButton } from '@/widgets/dashboard/management'
import { DashboardItem } from '@/widgets/dashboard-section'
import { ChartSkeleton } from '@/entities/charts'
import {
  setSubscriptions,
  useGetDashboardSubscriptionsQuery,
  useGetUserDashboardQuery,
} from '@/entities/quotes'
import { selectUserData } from '@/entities/user'
import { useAppDispatch, useAppSelector } from '@/shared/lib'
import { Paragraph, TypographyH2 } from '@/shared/ui'
import { skipToken } from '@reduxjs/toolkit/query'

const DashboardPage = () => {
  const dispatch = useAppDispatch()
  const { userId } = useParams() as { userId?: string }
  const user = useAppSelector(selectUserData)
  const { data: initialContent, isLoading, fulfilledTimeStamp } = useGetUserDashboardQuery(
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

  // fixme : сделать нормальную систему прав
  const writeAccess = !!((!userId && user) || (userId && user && parseInt(userId) === user.id))

  return (
    <>
      <div className="py-2 px-4 border-b border-border flex justify-between items-center gap-4 h-16">
        <div className='flex flex-col'>
          <TypographyH2>
            {userId ? `Дашборд пользователя ${userId}` : 'Мой дашборд'}
          </TypographyH2>
          <p className='text-muted-foreground'>Последнее обновление: {fulfilledTimeStamp ? new Date(fulfilledTimeStamp).toLocaleTimeString() : 'только что'}</p>
        </div>
        {writeAccess && <ManageDashboardButton />}
      </div>
      <div className="flex flex-col gap-4 items-center justify-center pt-6 lg:pt-0 px-2 md:px-4">
        <>
          {isLoading &&
            Array.from({ length: 20 }).map((_, idx) => (
              <div className="h-[300px] mb-2" key={idx}>
                <ChartSkeleton />
              </div>
            ))}
          {(!user || initialContent?.sections.length == 0) && (
            <div className='pt-10 text-center'>
              {!user ?
                <>
                <CircleX className='h-10 w-10 mx-auto mb-2' />
                <TypographyH2>Доступ запрещен</TypographyH2>
                <Paragraph className='text-muted-foreground mt-2'>Авторизуйтесь на сайте, чтобы создать свой дашборд</Paragraph>
                </>
              :
                <>
                <CircleHelp className='h-10 w-10 mx-auto mb-2' />
                <TypographyH2>Здесь ничего нет</TypographyH2>
                <Paragraph className='text-muted-foreground mt-2'>Данный дашборд пуст или не существует</Paragraph>
                </>
              }
            </div>
          )}
          {initialContent?.sections.map((section) => (
            <div className="w-full pb-8" key={section.section_name}>
              <div className="py-2 sticky top-0 z-40 bg-background">
                <TypographyH2>{section.section_name}</TypographyH2>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 pt-2">
                {section.data.map((item) => (
                  <DashboardItem key={item.quote_id} item={item} allowEdit={writeAccess} />
                ))}
              </div>
            </div>
          ))}
        </>
      </div>
      {/* Opens detailed drawer (dashboard quotation page) */}
      <Outlet />
    </>
  )
}

export { DashboardPage }
