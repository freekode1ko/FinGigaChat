import { useNavigate } from 'react-router-dom'

import {
  type QuotesSection,
  QuotesTable,
  QuotesTableRow,
} from '@/entities/quotes'
import { TradingViewMiniChart } from '@/entities/tradingview'
import { TypographyH2 } from '@/shared/ui'

interface QuotesSectionsListProps {
  sections?: Array<QuotesSection>
  openDetailsOnRowClick?: boolean
}

const QuotesSectionsList = ({ sections }: QuotesSectionsListProps) => {
  const navigate = useNavigate()

  return (
    <>
      {sections?.map((section, sectionIdx) => (
        <div key={sectionIdx} className="first:mt-4">
          <TypographyH2>{section.section_name}</TypographyH2>
          <QuotesTable headParams={section.section_params}>
            {section.data.map((row, rowIdx) => (
              <QuotesTableRow
                quote={row}
                priceChart={
                  row.tv_type && (
                    <TradingViewMiniChart
                      symbol={row.tv_type}
                      chartOnly
                      width="80"
                      height="60"
                      noTimeScale
                    />
                  )
                }
                onRowClick={() => navigate(`/quotes/${row.research_item_id}`)}
                key={rowIdx}
              />
            ))}
          </QuotesTable>
        </div>
      ))}
    </>
  )
}

export { QuotesSectionsList }
