import { useNavigate } from 'react-router-dom'

import { DashboardSubscriptionUpdateMenu } from '@/features/dashboard/update'
import { ChartSkeleton, CustomChart, mapFinancialData } from '@/entities/charts'
import {
  QuoteCard,
  type Quotes,
  useGetDashboardDataQuery,
} from '@/entities/quotes'
import { selectAppTheme } from '@/entities/theme'
import { useAppSelector } from '@/shared/lib'
import { SITE_MAP } from '@/shared/model'

interface LargeChartItemProps {
  item: Quotes
}

const LargeChartItem = ({ item }: LargeChartItemProps) => {
  const theme = useAppSelector(selectAppTheme)
  const navigate = useNavigate()
  const { data, isLoading } = useGetDashboardDataQuery({
    quoteId: item.quote_id,
    startDate: '01.01.2024',
  })

  if (isLoading)
    return (
      <div className="h-[220px]">
        <ChartSkeleton />
      </div>
    )

  if (!data || data?.data.length === 0)
    return (
      <QuoteCard
        name={item.name}
        value={0}
        change={0}
        type={item.view_type}
        ticker={item.ticker}
      />
    )

  return (
    <QuoteCard
      name={item.name}
      value={item.value}
      change={item.params[0].value}
      type={item.view_type}
      ticker={item.ticker}
      onCardClick={() =>
        navigate(`${SITE_MAP.dashboard}/quote/${item.quote_id}`)
      }
      graph={
        <CustomChart
          inputData={mapFinancialData([...data.data].reverse())}
          size="large"
          theme={theme}
        />
      }
      actionSlot={
        <DashboardSubscriptionUpdateMenu
          quoteId={item.quote_id}
          isActive={true}
          viewType={item.view_type}
          instantUpdate={true}
          display="dropdown"
        />
      }
    />
  )
}

export { LargeChartItem }
