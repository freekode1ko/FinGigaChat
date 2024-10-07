import { useNavigate } from 'react-router-dom'

import { ChartDemo, ChartSkeleton } from '@/entities/charts'
import {
  type DashboardSubscription,
  QuoteCard,
  useGetDashboardDataQuery,
} from '@/entities/quotes'
import { SITE_MAP } from '@/shared/model'

interface LargeChartItemProps {
  item: DashboardSubscription
}

const LargeChartItem = ({ item }: LargeChartItemProps) => {
  const navigate = useNavigate()
  const { data, isLoading, error } = useGetDashboardDataQuery({
    quoteId: item.id,
    startDate: '01.01.2024',
  })

  if (isLoading)
    return (
      <div className="h-[220px]">
        <ChartSkeleton />
      </div>
    )
  if (error || data?.data.length === 0)
    return (
      <QuoteCard
        name={item.name}
        value={0}
        change={0}
        type={item.type}
        ticker={item.ticker}
      />
    )

  const chartData = data?.data.map((d) => ({
    date: new Date(`${d.date}T00:00:00`),
    value: d.value,
    open: d.open,
    high: d.high,
    low: d.low,
    close: d.close,
    volume: d.volume,
  }))

  const latestData = data?.data[0]
  const previousData = data?.data[1]

  let dailyChange = 0
  if (latestData && previousData) {
    dailyChange =
      ((latestData.value - previousData.value) / previousData.value) * 100
  }

  return (
    <QuoteCard
      name={item.name}
      value={latestData?.value || 0}
      change={dailyChange}
      type={item.type}
      ticker={item.ticker}
      onCardClick={() => navigate(`${SITE_MAP.dashboard}/${item.id}`)}
      graph={<ChartDemo inputData={chartData!.reverse()} size="large" />}
    />
  )
}

export { LargeChartItem }
