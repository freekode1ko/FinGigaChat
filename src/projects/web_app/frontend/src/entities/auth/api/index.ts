import { baseApi } from '@/shared/api'
import { API_ENDPOINTS, KEEP_UNUSED_DATA_INF } from '@/shared/model'

import type { User } from '../model'

interface TelegramData {
  id: TelegramWebApps.WebAppUser['id']
  data: string
}

interface LoginInterface {
  email: string
}

interface VerifyCodeInteface extends LoginInterface {
  reg_code: string
}

export const authApi = baseApi.injectEndpoints({
  endpoints: (build) => ({
    getCurrentUser: build.query<User, void>({
      query: () => ({
        url: API_ENDPOINTS.auth + '/me',
        method: 'GET',
      }),
      keepUnusedDataFor: KEEP_UNUSED_DATA_INF,
    }),
    login: build.mutation<string, LoginInterface>({
      query: (data) => ({
        url: `${API_ENDPOINTS.auth}/login`,
        method: 'POST',
        body: data,
      }),
    }),
    verifyCode: build.mutation<string, VerifyCodeInteface>({
      query: (data) => ({
        url: `${API_ENDPOINTS.auth}/verify`,
        method: 'POST',
        body: data,
      }),
    }),
    validateTelegramData: build.mutation<string, TelegramData>({
      query: (data) => ({
        url: `${API_ENDPOINTS.auth}/validate_telegram`,
        method: 'POST',
        body: data,
      }),
    }),
  }),
})

export const {
  useValidateTelegramDataMutation,
  useLoginMutation,
  useVerifyCodeMutation,
  useLazyGetCurrentUserQuery,
} = authApi
