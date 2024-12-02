import { Outlet } from 'react-router-dom'

import { DashboardItem } from '@/widgets/dashboard-section'
import { ChartSkeleton } from '@/entities/charts'
import { useGetPopularDashboardQuery } from '@/entities/quotes/api'
import { GRAPH_POLLING_INTERVAL } from '@/shared/model'
import { TypographyH2 } from '@/shared/ui'

const PopularDashboardPage = () => {
  const { data: initialContent, isLoading, isFetching, fulfilledTimeStamp } = useGetPopularDashboardQuery(undefined, {
    pollingInterval: GRAPH_POLLING_INTERVAL,
    skipPollingIfUnfocused: true,
  })

  return (
    <>
      <div className="py-2 px-4 border-b border-border flex justify-between items-center gap-4 h-16">
        <div className='flex flex-col'>
          <TypographyH2>Избранные котировки</TypographyH2>
          <p className="text-muted-foreground">
            {isFetching
              ? 'Дашборд обновляется...'
              : `Последнее обновление: ${fulfilledTimeStamp ? new Date(fulfilledTimeStamp).toLocaleTimeString() : 'только что'}`}
          </p>
        </div>
      </div>
      <div className="flex flex-col gap-4 items-center justify-center pt-6 lg:pt-0 px-2 md:px-4">
        <>
          {isLoading &&
            Array.from({ length: 20 }).map((_, idx) => (
              <div className="h-[300px] mb-2" key={idx}>
                <ChartSkeleton />
              </div>
            ))}
          {initialContent?.sections.map((section) => (
            <div className="w-full pb-8" key={section.section_name}>
              <div className="py-2 sticky top-0 z-40 bg-background">
                <TypographyH2>{section.section_name}</TypographyH2>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 pt-2">
                {section.data.map((item) => (
                  <DashboardItem key={item.quote_id} item={item} allowEdit={false} />
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

export { PopularDashboardPage }
