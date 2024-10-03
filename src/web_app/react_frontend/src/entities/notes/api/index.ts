import { baseApi } from '@/shared/api'
import { API_ENDPOINTS, API_TAGS, KEEP_UNUSED_DATA_TEMP } from '@/shared/model'

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
      providesTags: [API_TAGS.notes],
    }),
    createNote: build.mutation<string, NoteRequest>({
      query: (note) => ({
        url: `${API_ENDPOINTS.notes}/${note.userId}`,
        method: 'POST',
        body: note.body,
      }),
      invalidatesTags: [API_TAGS.notes],
    }),
    updateNote: build.mutation<string, NoteUpdateRequest>({
      query: (note) => ({
        url: `${API_ENDPOINTS.notes}/${note.userId}/${note.noteId}`,
        method: 'PUT',
        body: note.body,
      }),
      invalidatesTags: [API_TAGS.notes],
    }),
    deleteNote: build.mutation<string, NoteDeleteRequest>({
      query: (note) => ({
        url: `${API_ENDPOINTS.notes}/${note.userId}/${note.noteId}`,
        method: 'DELETE',
      }),
      invalidatesTags: [API_TAGS.notes],
    }),
  }),
})

export const {
  useGetNotesQuery,
  useCreateNoteMutation,
  useDeleteNoteMutation,
  useUpdateNoteMutation,
} = notesApi
