import { z } from 'zod'

const createProductSchema = z.object({
  name: z.string().min(1, 'Название обязательно'),
  description: z.string().optional(),
  display_order: z.preprocess(
    (val) => parseInt(val as string, 10),
    z
      .number()
      .int('Порядковый номер должен быть целым числом')
      .nonnegative('Порядковый номер должен быть положительным')
  ),
  name_latin: z.string().optional(),
  parent_id: z.preprocess(
    (val) => parseInt(val as string, 10),
    z
      .number()
      .int('Идентификатор родителя должен быть целым числом')
      .nonnegative('Идентификатор не может быть отрицательным')
      .optional()
  ),
})

interface CreateProductFormData extends z.infer<typeof createProductSchema> {}

export { type CreateProductFormData, createProductSchema }
