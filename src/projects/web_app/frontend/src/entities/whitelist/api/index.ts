import { baseApi } from '@/shared/api'
import {
  API_ENDPOINTS,
  API_TAGS,
  PaginatedResponse,
  type PaginationProps,
} from '@/shared/model'

import type {
  CreateWhitelistUser,
  DeleteWhitelistUser,
  WhitelistUser,
} from '../model'

interface WhitelistQuery extends PaginationProps {
  email?: string
}

const whitelistApi = baseApi.injectEndpoints({
  endpoints: (build) => ({
    getWhitelist: build.query<PaginatedResponse<WhitelistUser>, WhitelistQuery>(
      {
        query: ({ page, size, email }) => ({
          url: API_ENDPOINTS.whitelist + '/',
          params: { page, size, email },
          method: 'GET',
        }),
        providesTags: [API_TAGS.whitelist],
      }
    ),
    createWhitelist: build.mutation<string, CreateWhitelistUser>({
      query: (body) => ({
        url: `${API_ENDPOINTS.whitelist}/`,
        method: 'POST',
        body: body,
      }),
      invalidatesTags: [API_TAGS.whitelist],
    }),
    deleteWhitelist: build.mutation<string, DeleteWhitelistUser>({
      query: ({ email }) => ({
        url: `${API_ENDPOINTS.whitelist}/` + email,
        method: 'DELETE',
      }),
      invalidatesTags: [API_TAGS.whitelist],
    }),
  }),
})

export const {
  useGetWhitelistQuery,
  useCreateWhitelistMutation,
  useDeleteWhitelistMutation,
} = whitelistApi
