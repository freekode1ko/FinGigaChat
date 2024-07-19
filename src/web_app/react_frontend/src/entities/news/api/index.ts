import { baseApi, ENDPOINTS } from '@/shared/api'

import type { News } from '../model'

const newsApi = baseApi.injectEndpoints({
  endpoints: (build) => ({
    getNews: build.query<{ news: Array<News> }, { page: number; size: number }>(
      {
        query: ({ page, size }) => ({
          url: `${ENDPOINTS.news}?page=${page}&size=${size}`,
          method: 'GET',
        }),
        keepUnusedDataFor: 120,
      }
    ),
  }),
})

export const { useGetNewsQuery } = newsApi
