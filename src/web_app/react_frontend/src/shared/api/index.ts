import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react'

export const baseApi = createApi({
  reducerPath: 'baseApi',
  baseQuery: fetchBaseQuery({ baseUrl: 'https://ai-bankir-helper-dev.ru/' }),
  endpoints: () => ({}),
})

export const ENDPOINTS = {
  popularQuotes: 'quotation/popular',
  dashboardQuotes: 'quotation/dashboard',
  news: 'news',
}
