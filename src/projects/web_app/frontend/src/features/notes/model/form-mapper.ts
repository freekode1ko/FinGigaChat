import type { CreateNote, Note } from '@/entities/notes'
import type { UserId } from '@/entities/auth'

export const mapUpdateFormData = (
  data: CreateNote,
  userId: UserId,
  noteId: Note['id']
) => {
  return {
    userId: userId,
    noteId: noteId,
    body: {
      client: data.client,
      description: data.description,
    },
  }
}

export const mapCreateFormData = (data: CreateNote, userId: UserId) => {
  return {
    userId: userId,
    body: {
      client: data.client,
      description: data.description,
    },
  }
}
