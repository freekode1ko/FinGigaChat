import { z } from 'zod'

import { type FullBroadcast, sendMessageSchema, useUpdateMessageMutation } from '@/entities/bot'

import { BaseMessageForm } from './base'

const UpdateMessageForm = ({
  broadcast,
  onSuccess,
}: {
  broadcast: FullBroadcast
  onSuccess: () => void
}) => {
  const [update, { isLoading }] = useUpdateMessageMutation()

  const handleUpdate = async (values: z.infer<typeof sendMessageSchema>) => {
    return update({
      broadcastId: broadcast.broadcast_id,
      data: values
    }).unwrap()
  }

  return (
    <BaseMessageForm
      onSuccess={onSuccess}
      onSubmit={handleUpdate}
      isLoading={isLoading}
      fieldValues={{message: broadcast.message_text, user_emails: []}}
      loadingText='Обновляем сообщения для выбранных пользователей...'
      successText='Сообщения успешно обновлены!'
      errorText='Ошибка при обновлении сообщений'
    />
  )
}

export { UpdateMessageForm }
