import type { CreateNote } from '@/entities/notes'
import type { UserId } from '@/entities/user'

export const mapFormData = (data: CreateNote, userId: UserId) => {
  return {
    userId: userId,
    body: {
      client: data.client,
      description: data.description,
    },
  }
}
