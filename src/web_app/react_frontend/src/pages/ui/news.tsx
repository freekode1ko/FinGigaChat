import { NewsCard, SkeletonNewsCard, useGetNewsQuery } from '@/entities/news'

const NewsPage = () => {
  const { data, isLoading, isError } = useGetNewsQuery()

  if (isError) return <div>Error</div>

  return (
    <div className="flex flex-col gap-2">
      {isLoading && (
        <>
          <SkeletonNewsCard />
          <SkeletonNewsCard />
          <SkeletonNewsCard />
        </>
      )}
      {data?.news.map((item, itemIdx) => <NewsCard {...item} key={itemIdx} />)}
    </div>
  )
}

export { NewsPage }
