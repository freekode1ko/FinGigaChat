import { QuotesSectionsList } from '@/widgets/quotes-sections-list'
import { useGetDashboardQuotesQuery } from '@/entities/quotes'

const DashboardPage = () => {
  const { data } = useGetDashboardQuotesQuery()

  return (
    <>
      <QuotesSectionsList sections={data?.sections} />
    </>
  )
}

export { DashboardPage }
