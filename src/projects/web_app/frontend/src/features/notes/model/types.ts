import { z } from 'zod'

import { noteFormSchema } from './zod-schema'

export interface CreateNoteFormData extends z.infer<typeof noteFormSchema> {}
