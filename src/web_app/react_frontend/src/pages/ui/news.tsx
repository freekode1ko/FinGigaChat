import { useCallback, useEffect, useRef, useState } from 'react'

import type { News } from '@/entities/news'
import { NewsCard, SkeletonNewsCard, useGetNewsQuery } from '@/entities/news'

const NewsPage = () => {
  // ВРЕМЕННОЕ РЕШЕНИЕ ДЛЯ INFINITE SCROLL
  const [page, setPage] = useState(1)
  const [news, setNews] = useState<Array<News>>([])
  const [isFetchingMore, setIsFetchingMore] = useState<boolean>(false)
  const { data, isLoading, isError } = useGetNewsQuery({ page, size: 10 })

  const observer = useRef<IntersectionObserver | null>(null)
  const lastNewsElementRef = useCallback((node: HTMLDivElement) => {
    if (news.length === 0 || isLoading || isFetchingMore) return;
    if (observer.current) observer.current.disconnect()
    observer.current = new IntersectionObserver((entries) => {
      if (entries[0].isIntersecting) {
        setIsFetchingMore(true)
        setPage((prevPage) => prevPage + 1)
      }
    })
    if (node) observer.current.observe(node)
  }, [isLoading, isFetchingMore, news])

  useEffect(() => {
    if (data?.news) {
      setNews((prevNews) => [...prevNews, ...data.news])
      setIsFetchingMore(false)
    }
  }, [data])

  if (isError) return <div>Error</div>

  return (
    <div className="flex flex-col gap-2">
      {news.map((item, itemIdx) => <NewsCard {...item} key={itemIdx} />)}
      {(isLoading || isFetchingMore) && (
        <>
          {Array.from({ length: 10 }).map((_, idx) => (
            <SkeletonNewsCard key={idx} />
          ))}
        </>
      )}
      <div ref={lastNewsElementRef} />
    </div>
  )
}

export { NewsPage }
