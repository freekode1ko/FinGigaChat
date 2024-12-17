import { CheckCheck, LoaderCircle, Send } from 'lucide-react'

import { useSendAnalyticsMutation } from '@/entities/analytics'
import { selectUserData } from '@/entities/auth'
import { useAppSelector } from '@/shared/lib'
import { Button } from '@/shared/ui'

/*
 * Кнопка для отправки аналитики в Telegram.
 * Не отображается в случае отсутствия Telegram ID.
 */
const SendAnalyticsButton = ({ analyticId }: { analyticId: number }) => {
  const user = useAppSelector(selectUserData)
  const [trigger, { isSuccess, isLoading }] = useSendAnalyticsMutation()

  if (!user) return

  if (isSuccess)
    return (
      <Button size="sm" variant="secondary" disabled>
        <CheckCheck className="h-4 w-4" /> Аналитика отправлена
      </Button>
    )

  if (isLoading)
    return (
      <Button size="sm" disabled>
        <LoaderCircle className="animate-spin h-4 w-4" /> Отправляем...
      </Button>
    )

  return (
    <Button
      size="sm"
      onClick={() => trigger({ reportId: analyticId, userId: user.id })}
    >
      <Send className="h-4 w-4" /> Отправить аналитику
    </Button>
  )
}

export { SendAnalyticsButton }
