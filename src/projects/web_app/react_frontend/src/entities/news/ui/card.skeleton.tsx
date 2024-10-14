import { Card, CardContent, CardHeader, Skeleton } from '@/shared/ui'

export const SkeletonNewsCard = () => {
  return (
    <Card>
      <CardHeader>
        <Skeleton className="h-8 w-5/6 rounded-full" />
        <Skeleton className="h-5 w-1/2 rounded-full" />
      </CardHeader>
      <CardContent>
        <Skeleton className="h-48" />
      </CardContent>
    </Card>
  )
}
