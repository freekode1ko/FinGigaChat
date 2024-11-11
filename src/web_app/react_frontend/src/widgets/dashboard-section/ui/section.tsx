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
    <div className="w-full pb-8">
      <div className="pt-2 pb-4">
        <TypographyH2>{section.section_name}</TypographyH2>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {section.data.map((item) => (
          <DashboardItem key={item.quote_id} item={item} />
        ))}
      </div>
    </div>
  )
}

export { DashboardSection }
