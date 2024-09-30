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

interface NoteDeleteRequest {
  userId: number
  noteId: Note['id']
}

interface NoteUpdateRequest {
  userId: number
  noteId: Note['id']
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
        url: `${API_ENDPOINTS.notes}/${note.userId}`,
        method: 'POST',
        body: note.body,
      }),
      invalidatesTags: [NOTES_API_TAG],
    }),
    updateNote: build.mutation<string, NoteUpdateRequest>({
      query: (note) => ({
        url: `${API_ENDPOINTS.notes}/${note.userId}/${note.noteId}`,
        method: 'PUT',
        body: note.body,
      }),
      invalidatesTags: [NOTES_API_TAG],
    }),
    deleteNote: build.mutation<string, NoteDeleteRequest>({
      query: (note) => ({
        url: `${API_ENDPOINTS.notes}/${note.userId}/${note.noteId}`,
        method: 'DELETE',
      }),
      invalidatesTags: [NOTES_API_TAG],
    }),
  }),
})

export const {
  useGetNotesQuery,
  useCreateNoteMutation,
  useDeleteNoteMutation,
  useUpdateNoteMutation,
} = notesApi
