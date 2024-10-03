import React, { useState } from 'react'

import {
  Button,
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
  const [isTruncated, setIsTruncated] = useState(true)
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
        <CardDescription
          className="mb-2"
          style={
            isTruncated
              ? {
                  overflow: 'hidden',
                  display: '-webkit-box',
                  WebkitBoxOrient: 'vertical',
                  WebkitLineClamp: 3,
                }
              : undefined
          }
        >
          {text}
        </CardDescription>
        {isTruncated ? (
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsTruncated(false)}
          >
            Подробнее
          </Button>
        ) : (
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsTruncated(true)}
          >
            Свернуть
          </Button>
        )}
      </CardContent>
    </Card>
  )
}
