import { Card, CardHeader, Skeleton } from '@/shared/ui'

export const SkeletonMeetingCard = () => {
  return (
    <Card>
      <CardHeader>
        <Skeleton className="h-8 w-5/6 rounded-full" />
        <Skeleton className="h-5 w-1/2 rounded-full" />
      </CardHeader>
    </Card>
  )
}
