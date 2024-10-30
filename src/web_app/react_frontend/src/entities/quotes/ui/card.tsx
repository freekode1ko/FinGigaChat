import React from 'react'

import { Badge, Card, CardTitle } from '@/shared/ui'

import type { DashboardSubscription, QuotesParams } from '../model'

interface QuoteCardProps
  extends Pick<DashboardSubscription, 'name' | 'type' | 'ticker'> {
  value: number
  params: Array<QuotesParams>
  onCardClick?: () => void
  graph?: React.ReactNode
  actionSlot?: React.ReactNode
}

const getChangeColor = (change: number): string => {
  if (change > 0) {
    return 'text-green-600 dark:text-green-500'
  } else if (change < 0) {
    return 'text-red-600 dark:text-red-500'
  } else {
    return 'text-gray-600 dark:text-gray-500'
  }
}

export const QuoteCard = ({
  name,
  value,
  ticker,
  params,
  type,
  graph,
  actionSlot,
  onCardClick,
}: QuoteCardProps) => {
  switch (type) {
    case 2:
      return (
        <Card className="flex flex-col items-center p-2 gap-2 lg:grid lg:grid-cols-3 relative shadow-none">
          {actionSlot && (
            <div className="absolute top-2 right-2 z-50 opacity-25 hover:opacity-100 p-2 bg-white dark:bg-dark-blue rounded-md">
              {actionSlot}
            </div>
          )}
          <div className="grid grid-cols-2 w-full items-center lg:items-start lg:gap-4 lg:flex lg:flex-col lg:col-span-1">
            <CardTitle
              className="text-lg col-span-1 cursor-pointer"
              onClick={onCardClick}
            >
              {name} {ticker && `(${ticker})`}
            </CardTitle>
            <div className="text-xl lg:text-2xl justify-end font-semibold flex flex-row lg:flex-col gap-2 lg:gap-0">
              <p>{value.toLocaleString('en-US')}</p>
              {params.length > 0 && 
                <p className={getChangeColor(params[0].value)}>
                {params[0].value.toLocaleString('en-US')}%
              </p>
              }
            </div>
          </div>
          <div className="w-full lg:col-span-2">{graph}</div>
        </Card>
      )
    case 3:
      return (
        <Card className="relative p-2 shadow-none">
          {actionSlot && (
            <div className="absolute top-2 right-2 z-50 opacity-25 hover:opacity-100 p-2 bg-white dark:bg-dark-blue rounded-md">
              {actionSlot}
            </div>
          )}
          <div className="grid grid-cols-4 items-center gap-2 p-1 lg:p-2">
            <CardTitle
              className="text-lg col-span-2 cursor-pointer"
              onClick={onCardClick}
            >
              {name} {ticker && `(${ticker})`}
            </CardTitle>
            <Badge variant="outline" className="col-span-1">
              {value.toLocaleString('en-US')}
            </Badge>
            {params.length > 0 && 
                <Badge
                  variant={
                    params[0].value < 0 ? 'destructive' : params[0].value > 0 ? 'positive' : 'default'
                  }
                  className="col-span-1"
                >
                  {params[0].value.toLocaleString('en-US')}%
                </Badge>
            }
          </div>
          {graph}
        </Card>
      )
    default:
      return (
        <Card className="relative p-2 shadow-none">
          {actionSlot && (
            <div className="absolute top-2 right-2 z-50 opacity-25 hover:opacity-100 p-2 bg-white dark:bg-dark-blue rounded-md">
              {actionSlot}
            </div>
          )}
          <div className="grid grid-cols-4 items-center gap-2 p-1 lg:p-2">
            <CardTitle
              className="text-md col-span-2 cursor-pointer"
              onClick={onCardClick}
            >
              {name} {ticker && `(${ticker})`}
            </CardTitle>
            <Badge variant="outline" className="col-span-1">
              {value.toLocaleString('en-US')}
            </Badge>
            {params.length > 0 && 
                <Badge
                  variant={
                    params[0].value < 0 ? 'destructive' : params[0].value > 0 ? 'positive' : 'default'
                  }
                  className="col-span-1"
                >
                  {params[0].value.toLocaleString('en-US')}%
                </Badge>
            }
          </div>
        </Card>
      )
  }
}
