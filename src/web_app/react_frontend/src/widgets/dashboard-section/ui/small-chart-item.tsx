import { ChartDemo } from '@/entities/charts'
import {
  type DashboardSubscription,
  useGetDashboardDataQuery,
} from '@/entities/quotes'

interface SmallChartItemProps {
  item: DashboardSubscription
}

const SmallChartItem = ({ item }: SmallChartItemProps) => {
  const { data, isLoading, error } = useGetDashboardDataQuery({
    quoteId: item.id,
  })

  if (isLoading) return <div>Loading {item.name}...</div>
  if (error) return <div>Error loading {item.name}</div>

  const chartData = data?.data.map((d) => ({
    date: new Date(`${d.date}T00:00:00`),
    value: d.value,
    open: d.open,
    high: d.high,
    low: d.low,
    close: d.close,
    volume: d.volume,
  }))

  return (
    <div className="p-2 rounded shadow">
      <ChartDemo inputData={chartData!} symbol={item.name} />
    </div>
  )
}

export { SmallChartItem }
