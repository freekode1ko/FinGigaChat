import type { DashboardSubscriptionSection } from '@/entities/quotes/model'
import { TypographyH2 } from '@/shared/ui'

import { DashboardItem } from './item'

interface DashboardSectionProps {
  section: DashboardSubscriptionSection
}

const DashboardSection = ({ section }: DashboardSectionProps) => {
  return (
    <>
      {section.subscription_items.filter((item) => item.active).length > 0 ? (
        <div className="w-full space-y-2">
          <TypographyH2>{section.section_name}</TypographyH2>
          <div className="grid grid-cols-1 gap-4">
            {section.subscription_items
              .filter((item) => item.active)
              .map((item) => (
                <DashboardItem key={item.id} item={item} />
              ))}
          </div>
        </div>
      ) : null}
    </>
  )
}

export { DashboardSection }
