import { baseApi } from '@/shared/api'
import { API_ENDPOINTS } from '@/shared/model'

interface SendMessage {
  message: string
}

export const botApi = baseApi.injectEndpoints({
  endpoints: (build) => ({
    sendMessage: build.mutation<string, SendMessage>({
      query: (data) => ({
        url: `${API_ENDPOINTS.bot}/messages`,
        method: 'POST',
        body: data,
      }),
    }),
  }),
})

export const { useSendMessageMutation } = botApi
