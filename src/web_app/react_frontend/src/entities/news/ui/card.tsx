import React from 'react'

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  Skeleton,
} from '@/shared/ui'

import type { News } from '../model'

interface NewsCardProps extends News {
  sendReportButton?: React.ReactNode
}

export const NewsCard = ({
  title,
  text,
  date,
  sendReportButton,
}: NewsCardProps) => {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        <div className="flex py-2 items-center justify-between">
          <small>{date}</small>
          {sendReportButton}
        </div>
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
