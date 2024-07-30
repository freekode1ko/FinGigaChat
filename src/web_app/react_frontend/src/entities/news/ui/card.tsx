import { CheckCheck, LoaderCircle, Send } from 'lucide-react'
import { useEffect, useState } from 'react'

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
  const [userId, setUserId] = useState<number>(0)
  const [trigger, { isSuccess, isLoading }] = useSendCibReportMutation()
  // ЭТО УБРАТЬ
  useEffect(() => {
    if (window.Telegram && window.Telegram.WebApp) {
      const user = window.Telegram.WebApp.initDataUnsafe?.user
      if (user) {
        setUserId(user.id)
      }
    }
  }, [])
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
          ) : isLoading ? (
            <Button
              size="sm"
              disabled
              onClick={() =>
                trigger({ newsId: news_id, tgUserId: userId.toString() })
              }
            >
              <LoaderCircle className="animate-spin h-4 w-4" /> Отправляем...
            </Button>
          ) : (
            <Button
              size="sm"
              onClick={() =>
                trigger({ newsId: news_id, tgUserId: userId.toString() })
              }
            >
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
