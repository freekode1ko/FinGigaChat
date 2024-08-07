import { QuotesTable, useGetDashboardQuotesQuery } from '@/entities/quotes'
import { TypographyH2 } from '@/shared/ui'

const DashboardPage = () => {
  const { data } = useGetDashboardQuotesQuery()

  return (
    <>
      {data?.sections.map((section, sectionIdx) => (
        <div key={sectionIdx} className="first:mt-4">
          <TypographyH2>{section.section_name}</TypographyH2>
          <QuotesTable data={section.data} params={section.section_params} />
        </div>
      ))}
    </>
  )
}

export { DashboardPage }
