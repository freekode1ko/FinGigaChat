import { SendCIBReportButton } from '@/features/send-cib-report'
import { type News, NewsCard, SkeletonNewsCard } from '@/entities/news'
import { PAGE_SIZE } from '@/shared/model'

interface NewsListProps {
  news?: Array<News>
  showSkeleton?: boolean
  showSendReportButton?: boolean
}

const NewsList = ({
  news,
  showSkeleton,
  showSendReportButton,
}: NewsListProps) => {
  return (
    <div className="flex flex-col gap-2">
      {news?.map((news, newsIdx) => (
        <NewsCard
          news_id={news.news_id}
          title={news.title}
          text={news.text}
          date={news.date}
          section={news.section}
          news_type={news.news_type}
          sendReportButton={
            showSendReportButton &&
            news.news_type == 'cib' && (
              <SendCIBReportButton newsId={news.news_id} />
            )
          }
          key={newsIdx}
        />
      ))}
      {showSkeleton &&
        Array.from({ length: PAGE_SIZE }).map((_, idx) => (
          <SkeletonNewsCard key={idx} />
        ))}
    </div>
  )
}

export { NewsList }
