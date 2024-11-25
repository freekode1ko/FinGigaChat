import { SendAnalyticsButton } from '@/features/send-analytics'
import {
  AnalyticCard,
  type Section,
  SkeletonAnalyticCard,
} from '@/entities/analytics'
import { PAGE_SIZE } from '@/shared/model'

interface NewsListProps {
  analytics?: Array<Section>
  showSkeleton?: boolean
  showSendAnalyticsButton?: boolean
}

const AnalyticsList = ({
  analytics,
  showSkeleton,
  showSendAnalyticsButton,
}: NewsListProps) => {
  return (
    <div className="flex flex-col gap-2">
      {analytics?.map((analytic) => (
        <AnalyticCard
          analytic_id={analytic.analytic_id}
          title={analytic.title}
          text={analytic.text}
          date={analytic.date}
          section={analytic.section}
          sendAnalyticButton={
            showSendAnalyticsButton && (
              <SendAnalyticsButton analyticId={analytic.analytic_id} />
            )
          }
          key={analytic.analytic_id}
        />
      ))}
      {showSkeleton &&
        Array.from({ length: PAGE_SIZE }).map((_, idx) => (
          <SkeletonAnalyticCard key={idx} />
        ))}
    </div>
  )
}

export { AnalyticsList }
