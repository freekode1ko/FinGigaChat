import { z } from 'zod'

export const loginFormSchema = z
  .object({
    email: z
      .string()
      .min(1, 'E-Mail не должен быть пустым')
      .email({ message: 'Адрес почтового ящика должен быть действительным' }),
  })
  .required()

export const confirmationFormSchema = z
  .object({
    code: z.string().min(6, {
      message: 'Одноразовый код должен составлять 6 символов.',
    }),
  })
  .required()
