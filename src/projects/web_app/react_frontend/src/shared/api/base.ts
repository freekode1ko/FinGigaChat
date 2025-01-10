import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react'

import { API_TAGS, DEV_API_URL } from '../model'

export const baseApi = createApi({
  reducerPath: 'baseApi',
  baseQuery: fetchBaseQuery({
    baseUrl:
      import.meta.env.VITE_DEBUG === 'true'
        ? DEV_API_URL
        : `${window.location.origin}/api/v1`,
  }),
  tagTypes: Object.values(API_TAGS),
  endpoints: () => ({}),
})
