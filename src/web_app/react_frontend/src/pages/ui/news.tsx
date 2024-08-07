import { NewsList } from '@/widgets/news-list'
import { useGetNewsQuery } from '@/entities/news'
import { useInfiniteScroll } from '@/shared/lib'
import { PAGE_SIZE } from '@/shared/model'

const NewsPage = () => {
  const { page, triggerRef } = useInfiniteScroll()
  const { data, isError, isFetching } = useGetNewsQuery({
    page,
    size: PAGE_SIZE,
  })

  if (isError) return <div>Error</div>

  return (
    <>
      <NewsList
        news={data?.news}
        showSkeleton={isFetching}
        showSendReportButton
      />
      <div ref={triggerRef} />
    </>
  )
}

export { NewsPage }
