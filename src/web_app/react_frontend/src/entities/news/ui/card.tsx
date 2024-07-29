import { CheckCheck, Send } from 'lucide-react'

import {
  Button,
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  Skeleton,
} from '@/shared/ui'

import { useSendCibReportMutation } from '../api'
import type { News } from '../model'

export const NewsCard = ({ title, text, date, news_id }: News) => {
  const [trigger, { isSuccess }] = useSendCibReportMutation()
  const tgUserId = window.Telegram.WebApp.initDataUnsafe.user.id
  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        <div className="flex py-2 items-center justify-between">
          <p className="text-accent-text-color">{date}</p>
          {isSuccess ? (
            <Button size="sm" variant="secondary" disabled>
              <CheckCheck className="h-4 w-4" /> Отчет отправлен
            </Button>
          ) : (
            <Button size="sm" onClick={() => trigger({newsId: news_id, tgUserId: tgUserId.toString()})}>
              <Send className="h-4 w-4" /> Отправить отчет CIB
            </Button>
          )}
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
