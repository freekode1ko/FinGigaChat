import { useNavigate, useParams } from 'react-router-dom'

import { NewsList } from '@/widgets/news-list'
import { CopyPageLinkButton } from '@/features/copy-page-link'
import { useGetNewsForQuotationQuery } from '@/entities/news'
import { selectAppTheme } from '@/entities/theme'
import { TradingViewAdvancedChart } from '@/entities/tradingview'
import { useAppSelector, useMediaQuery } from '@/shared/lib'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  Drawer,
  DrawerContent,
  DrawerHeader,
  DrawerTitle,
} from '@/shared/ui'

const QuoteDetailsPage = () => {
  const navigate = useNavigate()
  const isDesktop = useMediaQuery('(min-width: 768px)')
  const appTheme = useAppSelector(selectAppTheme)
  const { quotationId } = useParams() as { quotationId: string }
  const { data, isLoading } = useGetNewsForQuotationQuery({
    quotationId: quotationId,
  })

  if (isDesktop) {
    return (
      <Dialog open onOpenChange={() => navigate(-1)}>
        <DialogContent className="sm:max-w-[560px]">
          <DialogHeader>
            <DialogTitle>TVC:GOLD</DialogTitle>
          </DialogHeader>
          <div className="flex flex-col gap-4 max-h-[600px] overflow-y-auto">
            <TradingViewAdvancedChart
              symbol="TVC:GOLD"
              height="360"
              width="100%"
              theme={appTheme}
            />
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
            <DrawerTitle>TVC:GOLD</DrawerTitle>
          </DrawerHeader>
          <TradingViewAdvancedChart
            symbol="TVC:GOLD"
            height="360"
            width="100%"
            theme={appTheme}
          />
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
