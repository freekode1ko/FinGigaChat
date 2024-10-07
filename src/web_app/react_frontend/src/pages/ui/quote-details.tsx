import { useNavigate, useParams } from 'react-router-dom'

import { NewsList } from '@/widgets/news-list'
import { CopyPageLinkButton } from '@/features/copy-page-link'
import { ChartDemo, ChartSkeleton } from '@/entities/charts'
import { useGetNewsQuery } from '@/entities/news'
import {
  useGetDashboardDataQuery,
  useGetDashboardSubscriptionsQuery,
} from '@/entities/quotes'
import { selectUserData } from '@/entities/user'
import { useAppSelector, useMediaQuery } from '@/shared/lib'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  Drawer,
  DrawerContent,
  DrawerDescription,
  DrawerHeader,
  DrawerTitle,
  Skeleton,
} from '@/shared/ui'
import { skipToken } from '@reduxjs/toolkit/query'

const QuoteDetailsPage = () => {
  const navigate = useNavigate()
  const user = useAppSelector(selectUserData)
  const isDesktop = useMediaQuery('(min-width: 768px)')
  const { quotationId } = useParams() as { quotationId: string }
  const { data: subData } = useGetDashboardSubscriptionsQuery(
    user ? { userId: user.userId } : skipToken
  )
  const { data: finData } = useGetDashboardDataQuery({
    quoteId: parseInt(quotationId),
    startDate: '01.01.2024',
  })
  const { data, isLoading } = useGetNewsQuery()

  const chartData = finData?.data.map((d) => ({
    date: new Date(`${d.date}T00:00:00`),
    value: d.value,
    open: d.open,
    high: d.high,
    low: d.low,
    close: d.close,
    volume: d.volume,
  }))

  const currentQuote = subData?.subscription_sections
    .flatMap((section) => section.subscription_items)
    .find((item) => item.id === parseInt(quotationId))

  if (isDesktop) {
    return (
      <Dialog open onOpenChange={() => navigate(-1)}>
        <DialogContent className="sm:max-w-[560px]">
          <DialogHeader>
            {currentQuote ? (
              <>
                <DialogTitle>{currentQuote?.name}</DialogTitle>
                <DialogDescription>{currentQuote?.ticker}</DialogDescription>
              </>
            ) : (
              <Skeleton className="w-1/4 h-7" />
            )}
          </DialogHeader>
          <div className="flex flex-col gap-4 max-h-[600px] overflow-y-auto">
            <div className="max-h-[300px]">
              {finData ? (
                <ChartDemo
                  inputData={chartData!.reverse()}
                  size="large"
                  maxHeight={300}
                />
              ) : (
                <ChartSkeleton />
              )}
            </div>
            <NewsList news={data?.news} showSkeleton={isLoading} />
          </div>
        </DialogContent>
      </Dialog>
    )
  }

  return (
    <Drawer open onOpenChange={() => navigate(-1)}>
      <DrawerContent className="h-[90vh]">
        <div className="mx-auto w-full pt-6 text-text-color overflow-y-auto">
          <DrawerHeader>
            {currentQuote ? (
              <>
                <DrawerTitle>{currentQuote?.name}</DrawerTitle>
                <DrawerDescription>{currentQuote?.ticker}</DrawerDescription>
              </>
            ) : (
              <Skeleton className="w-1/4 h-7" />
            )}
          </DrawerHeader>
          <div className="max-h-[220px]">
            {finData ? (
              <ChartDemo
                inputData={chartData!.reverse()}
                size="large"
                maxHeight={220}
              />
            ) : (
              <ChartSkeleton />
            )}
          </div>
          <div className="p-2 flex-shrink-0 text-center">
            <CopyPageLinkButton />
          </div>
          <NewsList news={data?.news} showSkeleton={isLoading} />
        </div>
      </DrawerContent>
    </Drawer>
  )
}

export { QuoteDetailsPage }
