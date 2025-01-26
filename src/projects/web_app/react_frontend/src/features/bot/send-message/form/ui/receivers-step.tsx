import { Controller,useFormContext } from 'react-hook-form'

import { ReceiverSelector } from '@/features/bot/send-message/receivers'

export const ReceiverStep = () => {
  const { control } = useFormContext()

  return (
    <Controller
      name="user_emails"
      control={control}
      render={({ field }) => (
        <ReceiverSelector
          value={field.value}
          onChange={field.onChange}
        />
      )}
    />
  )
}
