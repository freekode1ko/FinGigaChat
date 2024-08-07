import { useState } from 'react'

import { NewsList } from '@/widgets/news-list'
import { useLazyGetNewsForQuotationQuery } from '@/entities/news'
import { selectAppTheme } from '@/entities/theme'
import {
  TradingViewAdvancedChart,
  TradingViewMiniChart,
} from '@/entities/tradingview'
import { useAppSelector } from '@/shared/lib'
import { Drawer, DrawerContent, DrawerHeader, DrawerTitle } from '@/shared/ui'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/shared/ui'

import { Quotes } from '../model'

interface QuotesTableProps {
  data: Array<Quotes>
  params: Array<string>
}

// ВРЕМЕННОЕ РЕШЕНИЕ: нужна декомпозиция

const QuotesTableRow = (quote: Quotes) => {
  const appTheme = useAppSelector(selectAppTheme)
  const [trigger, { data: newsData, isLoading: newsIsLoading }] =
    useLazyGetNewsForQuotationQuery()
  const [isDrawerOpen, setIsDrawerOpen] = useState(false)
  const handleDrawerOpen = (quotationId: number) => {
    setIsDrawerOpen(true)
    trigger({ quotationId: quotationId })
  }
  return (
    <TableRow>
      <TableCell className="cursor-pointer font-medium">
        <Drawer open={isDrawerOpen} onOpenChange={setIsDrawerOpen}>
          <span
            className="inline-flex items-center gap-2"
            onClick={() => handleDrawerOpen(quote.research_item_id)}
          >
            <img
              src={quote.image_path}
              alt={`${quote.name} image`}
              className="h-4 w-4"
            />
            {quote.name}
          </span>
          <DrawerContent className="h-[90vh]">
            <div className="mx-auto w-full pt-6 text-text-color overflow-y-auto">
              <DrawerHeader>
                <DrawerTitle>{quote.name}</DrawerTitle>
              </DrawerHeader>
              <TradingViewAdvancedChart
                symbol={quote.tv_type}
                height="360"
                theme={appTheme}
              />
              <NewsList news={newsData?.news} showSkeleton={newsIsLoading} />
            </div>
          </DrawerContent>
        </Drawer>
      </TableCell>
      <TableCell className="text-right">
        {quote.value ? quote.value.toLocaleString() : 'N/A'}
      </TableCell>
      {quote.params.map((param, paramIdx) => (
        <TableCell key={paramIdx} className="text-right">
          {param.value ? param.value.toLocaleString() : 'N/A'}
        </TableCell>
      ))}
      <TableCell className="text-right">
        {quote.tv_type ? (
          <TradingViewMiniChart
            symbol="TVC:GOLD"
            chartOnly
            width="80"
            height="60"
            autosize={false}
            noTimeScale
          />
        ) : (
          'N/A'
        )}
      </TableCell>
    </TableRow>
  )
}

export const QuotesTable = ({ data, params }: QuotesTableProps) => {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Название</TableHead>
          <TableHead className="text-right">Значение</TableHead>
          {params.map((param, paramIdx) => (
            <TableHead key={paramIdx} className="text-right">
              {param}
            </TableHead>
          ))}
          <TableHead className="text-right">График</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {data.map((item, itemIdx) => (
          <QuotesTableRow {...item} key={itemIdx} />
        ))}
      </TableBody>
    </Table>
  )
}
