import { ArrowRight } from 'lucide-react'
import { Link, Outlet } from 'react-router-dom'

import { FavoriteQuotes } from '@/widgets/favorite-quotes'
import { NewsList } from '@/widgets/news-list'
import { QuotesSectionsList } from '@/widgets/quotes-sections-list'
import { useGetNewsQuery } from '@/entities/news'
import { useGetPopularQuotesQuery } from '@/entities/quotes'
import { Button, TypographyH2 } from '@/shared/ui'

const QuotesPage = () => {
  const { data: quotesData } = useGetPopularQuotesQuery()
  const { data: newsData, isLoading: newsIsLoading } = useGetNewsQuery()

  return (
    <>
      <FavoriteQuotes />
      <QuotesSectionsList sections={quotesData?.sections} />
      <div className="mt-4">
        <TypographyH2>Последние новости</TypographyH2>
        <NewsList news={newsData?.news} showSkeleton={newsIsLoading} />
        <div className="py-2 text-center">
          <Button variant="ghost" size="sm" asChild>
            <Link to="/news">
              Все новости <ArrowRight className="h-4 w-4" />
            </Link>
          </Button>
        </div>
      </div>
      {/* Quote Details Drawer */}
      <Outlet />
    </>
  )
}

export { QuotesPage }
