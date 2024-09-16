import { baseApi } from '@/shared/api'
import {
  API_ENDPOINTS,
  KEEP_UNUSED_DATA_TEMP,
  NOTES_API_TAG,
} from '@/shared/model'

import type { CreateNote, Note } from '../model'

interface NoteRequest {
  userId: number
  body: CreateNote
}

const notesApi = baseApi.injectEndpoints({
  endpoints: (build) => ({
    getNotes: build.query<Array<Note>, { userId: number }>({
      query: ({ userId }) => ({
        url: `${API_ENDPOINTS.notes}/${userId}`,
        method: 'GET',
      }),
      keepUnusedDataFor: KEEP_UNUSED_DATA_TEMP,
      providesTags: [NOTES_API_TAG],
    }),
    createNote: build.mutation<string, NoteRequest>({
      query: (note) => ({
        url: `${API_ENDPOINTS.meetings}/${note.userId}`,
        method: 'POST',
        body: note.body,
      }),
      invalidatesTags: [NOTES_API_TAG],
    }),
  }),
})

export const { useGetNotesQuery, useCreateNoteMutation } = notesApi
