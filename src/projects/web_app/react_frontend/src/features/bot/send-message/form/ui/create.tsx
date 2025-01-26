import { useSendMessageMutation } from '@/entities/bot'

import { BaseMessageForm } from './base'

const SendMessageForm = ({ onSuccess }: { onSuccess: () => void }) => {
  const [send, { isLoading }] = useSendMessageMutation()

  return (
    <BaseMessageForm
      onSuccess={onSuccess}
      onSubmit={send}
      isLoading={isLoading}
      fieldValues={{message: '', user_emails: []}}
      loadingText='Формируем рассылку и отправляем сообщения пользователям...'
      successText='Рассылка успешно отправлена!'
      errorText='Ошибка при отправке рассылки'
    />
  )
}

export { SendMessageForm }
