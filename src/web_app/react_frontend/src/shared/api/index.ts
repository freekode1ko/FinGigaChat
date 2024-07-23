import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react'

const API_URL =
  import.meta.env.VITE_DEBUG === 'true'
    ? 'https://ai-bankir-helper-dev.ru/api/v1'
    : `${window.location.origin}/api/v1`

export const baseApi = createApi({
  reducerPath: 'baseApi',
  baseQuery: fetchBaseQuery({
    baseUrl: API_URL,
  }),
  endpoints: () => ({}),
})

export const ENDPOINTS = {
  popularQuotes: 'quotation/popular',
  dashboardQuotes: 'quotation/dashboard',
  news: 'news',
}
