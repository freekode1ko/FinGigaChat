import { QuotesSectionsList } from '@/widgets/quotes-sections-list'
import { ChartDemo } from '@/entities/charts'
import { ChartSkeleton } from '@/entities/charts/ui'
import { useGetPopularQuotesQuery } from '@/entities/quotes'

const DashboardPage = () => {
  const { data } = useGetPopularQuotesQuery()

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div className="grid grid-cols-2 gap-2">
        {['SBER', 'GOLD', 'GOLD'].map((symbol, symbolIdx) => (
          <div key={symbolIdx} className="col-span-1 min-h-36">
            <ChartDemo symbol={symbol} />
          </div>
        ))}
        <div className="col-span-1 min-h-36">
          <ChartSkeleton />
        </div>
      </div>
      <QuotesSectionsList sections={data?.sections} />
      <QuotesSectionsList sections={data?.sections} />
    </div>
  )
}

export { DashboardPage }
