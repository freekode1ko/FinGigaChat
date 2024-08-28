import { z } from 'zod'

import { meetingFormSchema } from './zod-schema'

export interface AddMeetingFormData extends z.infer<typeof meetingFormSchema> {}
