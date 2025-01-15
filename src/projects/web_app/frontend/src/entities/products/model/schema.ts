import { z } from 'zod'

import { fileSchema } from '@/shared/model'

import { MAX_PRODUCT_DOCUMENT_SIZE_MB } from './constants'

const entityFormSchema = z.object({
  name: z.string().min(1, { message: 'Название не может отсутствовать' }),
  description: z.string().optional(),
  parent_id: z.number().default(0),
  name_latin: z.string().optional(),
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
  description: z.string().optional(),
  files: fileSchema(MAX_PRODUCT_DOCUMENT_SIZE_MB).nullable(),
})

export { documentFormSchema, entityFormSchema }
