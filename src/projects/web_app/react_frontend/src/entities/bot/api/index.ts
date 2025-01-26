import { baseApi } from '@/shared/api'
import { API_ENDPOINTS, API_TAGS } from '@/shared/model'

import type { BroadcastWithVersions } from '../model'

interface SendMessage {
  message: string
  user_emails: Array<string>
}

interface UpdateMessage {
  message: string
}

interface GetMessagesResponse {
  messages: Array<BroadcastWithVersions>
  pagination: {
    page: number
    size: number
  }
}

interface GetFullMessageResponse {
  message: BroadcastWithVersions
}

export const botApi = baseApi.injectEndpoints({
  endpoints: (build) => ({
    sendMessage: build.mutation<string, SendMessage>({
      query: (data) => ({
        url: `${API_ENDPOINTS.bot}/messages`,
        method: 'POST',
        body: data,
      }),
      invalidatesTags: [API_TAGS.bot_messages],
    }),
    getMessages: build.query<
      GetMessagesResponse,
      { page: number; size: number }
    >({
      query: (params) => ({
        url: `${API_ENDPOINTS.bot}/messages`,
        method: 'GET',
        params,
      }),
      providesTags: [API_TAGS.bot_messages],
    }),
    getFullMessage: build.query<
      GetFullMessageResponse,
      { broadcastId: number }
    >({
      query: ({ broadcastId }) => ({
        url: `${API_ENDPOINTS.bot}/messages/${broadcastId}`,
        method: 'GET',
      }),
    }),
    deleteMessage: build.mutation<void, { broadcastId: number }>({
      query: ({ broadcastId }) => ({
        url: `${API_ENDPOINTS.bot}/messages/${broadcastId}`,
        method: 'DELETE',
      }),
      invalidatesTags: [API_TAGS.bot_messages],
    }),
    updateMessage: build.mutation<
      void,
      { broadcastId: number; data: UpdateMessage }
    >({
      query: ({ broadcastId, data }) => ({
        url: `${API_ENDPOINTS.bot}/messages/${broadcastId}`,
        method: 'PATCH',
        body: data,
      }),
      invalidatesTags: [API_TAGS.bot_messages],
    }),
  }),
})

export const {
  useSendMessageMutation,
  useGetMessagesQuery,
  useGetFullMessageQuery,
  useDeleteMessageMutation,
  useUpdateMessageMutation,
} = botApi
