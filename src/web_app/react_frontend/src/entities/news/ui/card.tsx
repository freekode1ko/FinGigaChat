import React from 'react'

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
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
