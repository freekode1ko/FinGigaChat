import React, { useState } from 'react'

import { Card, CardContent, CardDescription, CardTitle } from '@/shared/ui'

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
    <Card
      className="cursor-pointer hover:bg-card-foreground border-b border-border hover:border-none"
      onClick={() => setIsTruncated(!isTruncated)}
    >
      <CardContent className="flex flex-row items-center justify-between py-2">
        <p className="text-muted-foreground">{date}</p>
        <span onClick={(event) => event.stopPropagation()}>
          {sendReportButton}
        </span>
      </CardContent>
      <CardContent>
        <CardTitle>{title}</CardTitle>
        <CardDescription
          className="pt-4 transition-all duration-300"
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
      </CardContent>
    </Card>
  )
}
