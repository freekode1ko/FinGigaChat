import { DashboardSubscriptionUpdateMenu } from '@/features/dashboard/update'
import {
  DashboardSubscription,
  type FlattenedDashboardItem,
} from '@/entities/quotes'
import { cn } from '@/shared/lib'

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
      <div
        key={quote.id}
        className="flex items-center justify-between py-2 gap-2 border-b"
        style={style}
      >
        <span className={cn('ml-2', !quote.active && 'opacity-50')}>
          {quote.name}
        </span>
        <DashboardSubscriptionUpdateMenu
          quoteId={quote.id}
          isActive={quote.active}
          viewType={quote.type}
          instantUpdate={false}
        />
      </div>
    )
  }
}
