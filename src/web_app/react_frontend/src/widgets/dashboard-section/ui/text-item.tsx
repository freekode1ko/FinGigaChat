import { useNavigate } from 'react-router-dom'

import {
  type DashboardSubscription,
  QuoteCard,
  useGetDashboardDataQuery,
} from '@/entities/quotes'
import { SITE_MAP } from '@/shared/model'
import { Skeleton } from '@/shared/ui'

interface TextItemProps {
  item: DashboardSubscription
}

const TextItem = ({ item }: TextItemProps) => {
  const navigate = useNavigate()
  const previousDay = new Date(Date.now() - 86400000 * 14) // 14d
  const { data, isLoading, error } = useGetDashboardDataQuery({
    quoteId: item.id,
    startDate: previousDay.toLocaleDateString('ru-RU'),
  })

  if (isLoading) return <Skeleton className="w-full h-7" />
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
    />
  )
}

export { TextItem }
