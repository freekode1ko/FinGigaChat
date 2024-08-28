import { useNavigate, useParams } from 'react-router-dom'

import { NewsList } from '@/widgets/news-list'
import { CopyPageLinkButton } from '@/features/copy-page-link'
import { useGetNewsForQuotationQuery } from '@/entities/news'
import { selectAppTheme } from '@/entities/theme'
import { TradingViewAdvancedChart } from '@/entities/tradingview'
import { useAppSelector } from '@/shared/lib'
import { Drawer, DrawerContent, DrawerHeader, DrawerTitle } from '@/shared/ui'

const QuoteDetailsPage = () => {
  const navigate = useNavigate()
  const appTheme = useAppSelector(selectAppTheme)
  const { quotationId } = useParams() as { quotationId: string }
  const { data, isLoading } = useGetNewsForQuotationQuery({
    quotationId: quotationId,
  })

  return (
    <Drawer open onOpenChange={() => navigate('/quotes')}>
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
