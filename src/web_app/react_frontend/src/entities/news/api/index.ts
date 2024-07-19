import { baseApi, ENDPOINTS } from '@/shared/api'

import type { News } from '../model'

const newsApi = baseApi.injectEndpoints({
  endpoints: (build) => ({
    getNews: build.query<{ news: Array<News> }, void>({
      query: () => ({
        url: ENDPOINTS.news,
        method: 'GET',
      }),
      keepUnusedDataFor: 120,
    }),
  }),
})

export const { useGetNewsQuery } = newsApi
