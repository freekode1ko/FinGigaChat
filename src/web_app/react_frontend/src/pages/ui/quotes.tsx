import { QuotesTable, useGetPopularQuotesQuery } from '@/entities/quotes'

const QuotesPage = () => {
  const { data } = useGetPopularQuotesQuery()

  return (
    <>
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
