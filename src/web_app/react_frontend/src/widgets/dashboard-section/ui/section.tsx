import type { QuotesSection } from '@/entities/quotes/model'
import { TypographyH2 } from '@/shared/ui'

import { DashboardItem } from './item'

interface DashboardSectionProps {
  section: QuotesSection
}

const DashboardSection = ({ section }: DashboardSectionProps) => {
  if (section.data.length === 0) {
    return null
  }
  return (
    <div className="w-full space-y-2 mb-8 break-inside-avoid-column">
      <div className="py-2 z-50 sticky top-0 bg-white dark:bg-dark-blue">
        <TypographyH2>{section.section_name}</TypographyH2>
      </div>
      <div className="grid grid-cols-1 gap-4">
        {section.data.map((item) => (
          <DashboardItem key={item.quote_id} item={item} />
        ))}
      </div>
    </div>
  )
}

export { DashboardSection }
