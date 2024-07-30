import { ArrowRightCircle } from 'lucide-react'
import { Link } from 'react-router-dom'

import { NewsCard, SkeletonNewsCard, useGetNewsQuery } from '@/entities/news'
import { QuotesTable, useGetPopularQuotesQuery } from '@/entities/quotes'
import { PAGE_SIZE } from '@/shared/model'
import { TradingViewWidget } from '@/shared/ui'

const QuotesPage = () => {
  const TV_DATA = [
    'FX_IDC:CNYRUB',
    'FX_IDC:USDCNY',
    'BLACKBULL:BRENT',
    'TVC:GOLD',
  ]
  const { data: quotesData } = useGetPopularQuotesQuery()
  const { data: newsData, isLoading: newsIsLoading } = useGetNewsQuery({
    page: 1,
    size: PAGE_SIZE,
  })

  return (
    <>
      <div className="grid grid-cols-2 gap-4 pb-4">
        {TV_DATA.map((symbol, symbolIdx) => (
          <div key={symbolIdx} className="col-span-1">
            <TradingViewWidget symbol={symbol} />
          </div>
        ))}
      </div>
      {quotesData?.sections.map((section, sectionIdx) => (
        <div key={sectionIdx} className="first:mt-4">
          <h2 className="scroll-m-20 text-2xl font-semibold tracking-tight text-hint-color">
            {section.section_name}
          </h2>
          <QuotesTable data={section.data} params={section.section_params} />
        </div>
      ))}
      <div className="mt-4">
        <h2 className="scroll-m-20 text-2xl font-semibold tracking-tight text-hint-color">
          Последние новости
        </h2>
        <div className="flex flex-col gap-2">
          {newsData?.news.map((item, itemIdx) => (
            <NewsCard {...item} key={itemIdx} />
          ))}
          {newsIsLoading &&
            Array.from({ length: PAGE_SIZE }).map((_, idx) => (
              <SkeletonNewsCard key={idx} />
            ))}
        </div>
        <div className="mx-auto py-2">
          <Link
            to="/news"
            className="inline-flex items-center text-hint-color hover:text-accent-text-color no-underline"
          >
            Все новости
            <ArrowRightCircle className="h-4 w-4" />
          </Link>
        </div>
      </div>
    </>
  )
}

export { QuotesPage }
