import { useNavigate } from 'react-router-dom'

import { DashboardSubscriptionUpdateMenu } from '@/features/dashboard/update'
import { QuoteCard, Quotes } from '@/entities/quotes'
import { SITE_MAP } from '@/shared/model'

interface TextItemProps {
  item: Quotes
}

const TextItem = ({ item }: TextItemProps) => {
  const navigate = useNavigate()

  return (
    <QuoteCard
      name={item.name}
      value={item.value}
      params={item.params}
      type={item.view_type}
      ticker={item.ticker}
      onCardClick={() =>
        navigate(`${SITE_MAP.dashboard}/quote/${item.quote_id}`)
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

export { TextItem }
