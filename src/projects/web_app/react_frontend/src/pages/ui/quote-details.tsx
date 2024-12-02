import { useNavigate, useParams } from 'react-router-dom'

// import { NewsList } from '@/widgets/news-list'
import { ChartSkeleton, CustomChart, mapFinancialData } from '@/entities/charts'
// import { useGetNewsQuery } from '@/entities/news'
import {
  useGetDashboardDataQuery,
  useGetDashboardSubscriptionsQuery,
} from '@/entities/quotes'
import { selectAppTheme } from '@/entities/theme'
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
  const theme = useAppSelector(selectAppTheme)
  const navigate = useNavigate()
  const user = useAppSelector(selectUserData)
  const isDesktop = useMediaQuery('(min-width: 768px)')
  const { quotationId } = useParams() as { quotationId: string }
  const { data: subData } = useGetDashboardSubscriptionsQuery(
    user ? { userId: user.id } : skipToken
  )
  const { data: finData } = useGetDashboardDataQuery({
    quoteId: parseInt(quotationId),
    startDate: '01.01.2024',
  })
  // const { data, isLoading } = useGetNewsQuery()

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
          <div className="relative h-[300px]">
            {finData ? (
              finData.data?.length > 2 ? (
                <CustomChart
                  inputData={mapFinancialData([...finData.data].reverse())}
                  size="large"
                  height={300}
                  theme={theme}
                />
              ) : (
                <p className="text-muted-foreground text-center m-0 absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2">
                  График по этому инструменту сейчас недоступен
                </p>
              )
            ) : (
              <ChartSkeleton />
            )}
          </div>
        </DialogContent>
      </Dialog>
    )
  }

  return (
    <Drawer open onOpenChange={() => navigate(-1)}>
      <DrawerContent className="h-[370px]">
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
          <div className="relative h-[220px]">
            {finData ? (
              finData.data?.length > 2 ? (
                <CustomChart
                  inputData={mapFinancialData([...finData.data].reverse())}
                  size="large"
                  height={220}
                  theme={theme}
                />
              ) : (
                <p className="text-muted-foreground text-center m-0 absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2">
                  График по этому инструменту сейчас недоступен
                </p>
              )
            ) : (
              <ChartSkeleton />
            )}
          </div>
        </div>
      </DrawerContent>
    </Drawer>
  )
}

export { QuoteDetailsPage }
