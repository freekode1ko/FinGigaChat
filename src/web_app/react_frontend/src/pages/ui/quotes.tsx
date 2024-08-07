import { ArrowRight } from 'lucide-react'
import { Link } from 'react-router-dom'

import { FavoriteQuotes } from '@/widgets/favorite-quotes'
import { NewsList } from '@/widgets/news-list'
import { useGetNewsForMainQuery } from '@/entities/news'
import { QuotesTable, useGetPopularQuotesQuery } from '@/entities/quotes'
import { TypographyH2 } from '@/shared/ui'

const QuotesPage = () => {
  const { data: quotesData } = useGetPopularQuotesQuery()
  const { data: newsData, isLoading: newsIsLoading } = useGetNewsForMainQuery()

  return (
    <>
      <FavoriteQuotes />
      {quotesData?.sections.map((section, sectionIdx) => (
        <div key={sectionIdx} className="first:mt-4">
          <TypographyH2>{section.section_name}</TypographyH2>
          <QuotesTable data={section.data} params={section.section_params} />
        </div>
      ))}
      <div className="mt-4">
        <TypographyH2>Последние новости</TypographyH2>
        <NewsList news={newsData?.news} showSkeleton={newsIsLoading} />
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
