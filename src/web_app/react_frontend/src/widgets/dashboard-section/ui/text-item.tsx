import {
  type DashboardSubscription,
  useGetDashboardDataQuery,
} from '@/entities/quotes'

interface TextItemProps {
  item: DashboardSubscription
}

const TextItem = ({ item }: TextItemProps) => {
  const { data, isLoading, error } = useGetDashboardDataQuery({
    quoteId: item.id,
  })

  if (isLoading) return <div>Loading {item.name}...</div>
  if (error) return <div>Error loading {item.name}</div>

  const latestData = data?.data[data.data.length - 1]

  return (
    <div className="p-4 rounded shadow">
      <p className="text-lg font-medium">
        {item.name}: {latestData?.value}
      </p>
    </div>
  )
}

export { TextItem }
