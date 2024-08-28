import type { UserId } from '@/entities/user'

import type { AddMeetingFormData } from '../model'

export const mapFormData = (data: AddMeetingFormData, userId: UserId) => {
  return {
    user_id: userId,
    theme: data.theme,
    description: data.description,
    timezone: parseInt(data.timezone),
    date_start: new Date(data.date_start).toISOString(),
    date_end: new Date(data.date_end).toISOString(),
  }
}
