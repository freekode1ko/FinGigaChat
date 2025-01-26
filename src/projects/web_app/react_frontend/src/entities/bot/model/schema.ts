import { z } from 'zod'

// import { fileSchema } from '@/shared/model'

export const sendMessageSchema = z.object({
  message: z
    .string()
    .min(20, { message: 'Текст рассылки не может быть таким коротким' }),
  // files: fileSchema(10, 10),
  user_emails: z.array(z.string()).min(1, {
    message: 'Необходимо выбрать хотя бы одного получателя рассылки',
  }),
})
