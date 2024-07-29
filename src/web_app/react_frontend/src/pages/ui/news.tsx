import { useCallback, useRef, useState } from 'react'

import { NewsCard, SkeletonNewsCard, useGetNewsQuery } from '@/entities/news'
import { PAGE_SIZE } from '@/shared/model'

const NewsPage = () => {
  const [page, setPage] = useState(1)
  const { data, isLoading, isError, isFetching } = useGetNewsQuery({
    page,
    size: PAGE_SIZE,
  })

  const observer = useRef<Optional<IntersectionObserver>>(null)
  const lastNewsElementRef = useCallback(
    (node: HTMLDivElement) => {
      if (isLoading) return
      if (observer.current) observer.current.disconnect()
      observer.current = new IntersectionObserver((entries) => {
        if (entries[0].isIntersecting) {
          setPage((prevPage) => prevPage + 1)
        }
      })
      if (node) observer.current.observe(node)
    },
    [isLoading]
  )

  if (isError) return <div>Error</div>

  return (
    <div className="flex flex-col gap-2">
      {data?.news.map((item, itemIdx) => <NewsCard {...item} key={itemIdx} />)}
      {isFetching &&
        Array.from({ length: PAGE_SIZE }).map((_, idx) => (
          <SkeletonNewsCard key={idx} />
        ))}
      <div ref={lastNewsElementRef} />
    </div>
  )
}

export { NewsPage }
