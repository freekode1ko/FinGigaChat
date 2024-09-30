import type { DashboardSubscriptionSection } from '@/entities/quotes/model'

import { DashboardItem } from './item'

interface DashboardSectionProps {
  section: DashboardSubscriptionSection
}

const DashboardSection = ({ section }: DashboardSectionProps) => {
  return (
    <div className="w-full">
      <h2 className="text-2xl font-bold mb-4">{section.section_name}</h2>
      <div className="grid grid-cols-1 gap-4">
        {section.subscription_items
          .filter((item) => item.active)
          .map((item) => (
            <DashboardItem key={item.id} item={item} />
          ))}
      </div>
    </div>
  )
}

export { DashboardSection }
