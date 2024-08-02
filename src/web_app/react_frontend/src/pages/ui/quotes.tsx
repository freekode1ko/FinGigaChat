import { ArrowRight } from 'lucide-react'
import { Link } from 'react-router-dom'

import { FavoriteQuotes } from '@/widgets/favorite-quotes'
import {
  NewsCard,
  SkeletonNewsCard,
  useGetNewsForMainQuery,
} from '@/entities/news'
import { QuotesTable, useGetPopularQuotesQuery } from '@/entities/quotes'
import { PAGE_SIZE } from '@/shared/model'

const QuotesPage = () => {
  const { data: quotesData } = useGetPopularQuotesQuery()
  const { data: newsData, isLoading: newsIsLoading } = useGetNewsForMainQuery()

  return (
    <>
      <FavoriteQuotes />
      {quotesData?.sections.map((section, sectionIdx) => (
        <div key={sectionIdx} className="first:mt-4">
          <h2 className="scroll-m-20 text-2xl font-semibold tracking-tight text-hint-color">
            {section.section_name}
          </h2>
          <QuotesTable data={section.data} params={section.section_params} />
        </div>
      ))}
      <div className="mt-4">
        <h2 className="scroll-m-20 text-2xl font-semibold tracking-tight text-hint-color mb-2">
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
        <div className="py-2 text-center">
          <Link
            to="/news"
            className="mx-auto inline-flex items-center gap-1 text-hint-color hover:text-accent-text-color no-underline"
          >
            Все новости
            <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
      </div>
    </>
  )
}

export { QuotesPage }
