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
    return 'text-destructive'
  } else {
    return 'text-secondary'
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
    case 1:
      return (
        <Card className="bg-secondary border border-border relative p-2 shadow-none hover:bg-background">
          <div className="flex items-center gap-4 p-1 lg:p-2">
            <div className='flex flex-col flex-[2] min-w-0'>
              <div className='flex flex-row flex-nowrap gap-1'>
                {actionSlot}
                <CardTitle className="text-md cursor-pointer" onClick={onCardClick} style={{
                  overflow: 'hidden',
                  display: '-webkit-box',
                  WebkitBoxOrient: 'vertical',
                  WebkitLineClamp: 2,
                }}>
                  {ticker ? ticker : name}
                </CardTitle>
              </div>
              {ticker && <p className='text-muted-foreground'>{name}</p>}
            </div>
            {
              graph && <div className='flex-[3] min-w-0'>{graph}</div>
            }
            <div className='flex flex-col items-end flex-none gap-1'>
              <p className="text-lg font-medium">
                {value ? value.toLocaleString('en-US') : '0'}
              </p>
              {params.length > 0 && 
                <Badge
                  variant={
                    params[0].value < 0 ? 'destructive' : params[0].value > 0 ? 'positive' : 'default'
                  }
                >
                  {params[0].value.toLocaleString('en-US')}%
                </Badge>
              }
            </div>
          </div>
        </Card>
      )
  
    default:
      return (
        <Card className="flex flex-col items-center p-2 gap-2 lg:grid lg:grid-cols-3 relative shadow-none bg-secondary border border-border hover:bg-background">
          <div className="grid grid-cols-2 w-full items-center lg:items-start lg:gap-4 lg:flex lg:flex-col lg:justify-between lg:col-span-1 h-full">
            <div className='flex flex-col col-span-1'>
              <div className='flex flex-row flex-nowrap gap-1'>
                {actionSlot}
                <CardTitle className="text-md cursor-pointer" onClick={onCardClick} style={{
                  overflow: 'hidden',
                  display: '-webkit-box',
                  WebkitBoxOrient: 'vertical',
                  WebkitLineClamp: 2,
                }}>
                  {ticker ? ticker : name}
                </CardTitle>
              </div>
              {ticker && <p className='text-muted-foreground'>{name}</p>}
            </div>
            <div className="text-xl lg:text-2xl justify-end font-semibold flex flex-row lg:flex-col gap-2 lg:gap-0">
              <p>{value ? value.toLocaleString('en-US') : '0'}</p>
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
  }
}
