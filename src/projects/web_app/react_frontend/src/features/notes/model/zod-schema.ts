import { z } from 'zod'

export const noteFormSchema = z
  .object({
    client: z.string().min(1, 'Укажите название заметки'),
    description: z.string().min(1, 'Добавьте текст заметки'),
  })
  .required()
