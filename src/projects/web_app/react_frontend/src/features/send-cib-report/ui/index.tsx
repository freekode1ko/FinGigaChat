import { CheckCheck, LoaderCircle, Send } from 'lucide-react'

import { useSendCibReportMutation } from '@/entities/news'
import { selectUserData } from '@/entities/user'
import { useAppSelector } from '@/shared/lib'
import { Button } from '@/shared/ui'

/*
 * Кнопка для отправки отчета CIB в Telegram.
 * Не отображается в случае отсутствия Telegram ID.
 */
const SendCIBReportButton = ({ newsId }: { newsId: string }) => {
  const user = useAppSelector(selectUserData)
  const [trigger, { isSuccess, isLoading }] = useSendCibReportMutation()

  if (!user) return

  if (isSuccess)
    return (
      <Button size="sm" variant="secondary" disabled>
        <CheckCheck className="h-4 w-4" /> Отчет отправлен
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
      onClick={() => trigger({ newsId: newsId, tgUserId: user.id })}
    >
      <Send className="h-4 w-4" /> Отправить отчет CIB
    </Button>
  )
}

export { SendCIBReportButton }
