import { z } from 'zod'

import { fileSchema } from '@/shared/model'

import { MAX_INDUSTRY_DOCUMENT_SIZE_MB } from './constants'

const entityFormSchema = z.object({
  name: z.string().min(1, { message: 'Название не может отсутствовать' }),
  display_order: z.coerce
    .number({
      invalid_type_error: 'Порядок должен быть целым числом',
    })
    .int()
    .positive()
    .min(1, { message: 'Порядок не может быть меньше 1' }),
})

const documentFormSchema = z.object({
  name: z.string(),
  files: fileSchema(MAX_INDUSTRY_DOCUMENT_SIZE_MB),
})

export { documentFormSchema, entityFormSchema }
