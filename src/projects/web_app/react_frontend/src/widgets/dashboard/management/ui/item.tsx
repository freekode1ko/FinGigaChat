import { DashboardSubscriptionUpdateMenu } from '@/features/dashboard/update'
import {
  DashboardSubscription,
  type FlattenedDashboardItem,
} from '@/entities/quotes'

interface ManageItemProps {
  index: number
  data: Array<FlattenedDashboardItem>
  style: React.CSSProperties
}

export const ItemRow = ({ index, data, style }: ManageItemProps) => {
  const item = data[index]
  if (item.type === 'section') {
    return (
      <div key={item.sectionName} className="mb-2 sticky top-0" style={style}>
        <h2 className="text-xl font-semibold py-2">{item.sectionName}</h2>
      </div>
    )
  } else if (item.type === 'item') {
    const quote = item.item as DashboardSubscription
    return (
      <div className='border-b border-border h-[56px]' style={style}>
        <DashboardSubscriptionUpdateMenu
          quoteId={quote.id}
          quoteName={quote.name}
          isActive={quote.active}
          viewType={quote.type}
        />
      </div>
    )
  }
}
