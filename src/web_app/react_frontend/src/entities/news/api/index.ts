import { baseApi } from '@/shared/api'
import {
  API_ENDPOINTS,
  KEEP_UNUSED_DATA_TEMP,
  type PaginationProps,
} from '@/shared/model'

import type { News } from '../model'

interface GetNewsQuery extends PaginationProps {}

interface GetNewsForQuotationQuery {
  quotationId: string
}

interface NewsResponse {
  news: Array<News>
}

const newsApi = baseApi.injectEndpoints({
  endpoints: (build) => ({
    getInfiniteNews: build.query<NewsResponse, GetNewsQuery>({
      query: ({ page, size }) => ({
        url: `${API_ENDPOINTS.news}?page=${page}&size=${size}`,
        method: 'GET',
      }),
      serializeQueryArgs: ({ endpointName }) => {
        return endpointName
      },
      merge: (currentCache, newItems) => {
        currentCache.news.push(...newItems.news)
      },
      forceRefetch({ currentArg, previousArg }) {
        return currentArg !== previousArg
      },
      keepUnusedDataFor: KEEP_UNUSED_DATA_TEMP,
    }),
    getNews: build.query<NewsResponse, void>({
      query: () => ({
        url: API_ENDPOINTS.news,
        method: 'GET',
      }),
      keepUnusedDataFor: KEEP_UNUSED_DATA_TEMP,
    }),
    getNewsForQuotation: build.query<NewsResponse, GetNewsForQuotationQuery>({
      query: ({ quotationId }) => ({
        url: `${API_ENDPOINTS.news}/${quotationId}`,
        method: 'GET',
      }),
      keepUnusedDataFor: KEEP_UNUSED_DATA_TEMP,
    }),
    sendCibReport: build.mutation<void, { tgUserId: string; newsId: string }>({
      query: ({ tgUserId, newsId }) => ({
        url: `${API_ENDPOINTS.news}/send?user_id=${tgUserId}&news_id=${newsId}`,
        method: 'POST',
      }),
    }),
  }),
})

export const {
  useGetNewsQuery,
  useGetNewsForQuotationQuery,
  useSendCibReportMutation,
  useGetInfiniteNewsQuery,
} = newsApi
