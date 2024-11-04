import React from 'react'

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/shared/ui'

import type { Section } from '../model'

interface NewsCardProps extends Section {
  sendAnalyticButton?: React.ReactNode
}

export const AnalyticCard = ({
  title,
  text,
  date,
  sendAnalyticButton,
}: NewsCardProps) => {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        <div className="flex py-2 items-center justify-between">
          <small>{date}</small>
          {sendAnalyticButton}
        </div>
      </CardHeader>
      <CardContent>
        <CardDescription>{text}</CardDescription>
      </CardContent>
    </Card>
  )
}
