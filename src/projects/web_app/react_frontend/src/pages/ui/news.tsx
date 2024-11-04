import { NewsList } from '@/widgets/news-list'
import { useGetInfiniteNewsQuery } from '@/entities/news'
import { useInfiniteScroll } from '@/shared/lib'
import { PAGE_SIZE } from '@/shared/model'
import { ShowMoreButton } from '@/shared/ui'

const NewsPage = () => {
  const { page, triggerRef } = useInfiniteScroll()
  const { data, isFetching } = useGetInfiniteNewsQuery({
    page,
    size: PAGE_SIZE,
  })

  return (
    <div className='pt-10 pb-4'>
      <NewsList
        news={data?.news}
        showSkeleton={isFetching}
        showSendReportButton
      />
      <ShowMoreButton ref={triggerRef} />
    </div>
  )
}

export { NewsPage }
