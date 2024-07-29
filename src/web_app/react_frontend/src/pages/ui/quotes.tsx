import { QuotesTable, useGetPopularQuotesQuery } from '@/entities/quotes'
import { TradingViewWidget } from '@/shared/ui'

const QuotesPage = () => {
  const TV_DATA = ['MOEX:SBER', 'MOEX:RGBI', 'BLACKBULL:BRENT', 'TVC:GOLD']
  const { data } = useGetPopularQuotesQuery()

  return (
    <>
      <div className="grid grid-cols-2 gap-4 pb-4">
        {TV_DATA.map((symbol, symbolIdx) => (
          <div key={symbolIdx} className="col-span-1">
            <TradingViewWidget symbol={symbol} />
          </div>
        ))}
      </div>
      {data?.sections.map((section, sectionIdx) => (
        <div key={sectionIdx} className="first:mt-4">
          <h2 className="scroll-m-20 text-2xl font-semibold tracking-tight text-hint-color">
            {section.section_name}
          </h2>
          <QuotesTable data={section.data} params={section.section_params} />
        </div>
      ))}
    </>
  )
}

export { QuotesPage }
