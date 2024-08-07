import { CheckCheck, LoaderCircle, Send } from 'lucide-react'

import { useSendCibReportMutation } from '@/entities/news'
import { useInitData } from '@/shared/lib'
import { Button } from '@/shared/ui'

const SendCIBReportButton = ({ newsId }: { newsId: string }) => {
  const [trigger, { isSuccess, isLoading }] = useSendCibReportMutation()
  const [userData] = useInitData()

  // if (!userData?.user) return

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
      onClick={() =>
        trigger({ newsId: newsId, tgUserId: userData!.user!.id.toString() })
      }
    >
      <Send className="h-4 w-4" /> Отправить отчет CIB
    </Button>
  )
}

export { SendCIBReportButton }
