import { z } from 'zod'

import { fileSchema } from '@/shared/model'

import { MAX_ANALYTICS_DOCUMENT_SIZE_MB } from './constants'

const analyticsFormSchema = z.object({
  title: z.string().optional(),
  text: z.string(),
  files: fileSchema(MAX_ANALYTICS_DOCUMENT_SIZE_MB).nullable(),
})

export { analyticsFormSchema }
