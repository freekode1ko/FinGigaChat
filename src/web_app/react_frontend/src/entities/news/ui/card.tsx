import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  Skeleton,
} from '@/shared/ui'

import type { News } from '../model'

export const NewsCard = ({ title, text, date }: News) => {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        <CardDescription className="text-accent-text-color">
          {date}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <CardDescription>{text}</CardDescription>
      </CardContent>
    </Card>
  )
}

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
