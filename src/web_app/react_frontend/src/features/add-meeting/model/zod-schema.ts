import { z } from 'zod'

export const meetingFormSchema = z.object({
  theme: z.string().min(1, 'Обязательно укажите тему встречи'),
  date_start: z.string().min(16, 'Укажите время начала встречи'),
  date_end: z.string().min(16, 'Укажите время окончания встречи'),
  description: z.string().min(1, 'Добавьте описание встречи'),
  timezone: z
    .number()
    .min(-12, 'Некорректная временная зона')
    .max(14, 'Некорректная временная зона'),
})
