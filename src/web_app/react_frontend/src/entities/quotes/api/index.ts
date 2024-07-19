import { baseApi, ENDPOINTS } from '@/shared/api'

import type { Quotes } from '../model'

interface QuotesResponse {
  section_name: string
  section_params: Array<string>
  data: Array<Quotes>
}

const newsApi = baseApi.injectEndpoints({
  endpoints: (build) => ({
    getPopularQuotes: build.query<{ sections: Array<QuotesResponse> }, void>({
      query: () => ({
        url: ENDPOINTS.popularQuotes,
        method: 'GET',
      }),
      keepUnusedDataFor: 120,
    }),
    getDashboardQuotes: build.query<{ sections: Array<QuotesResponse> }, void>({
      query: () => ({
        url: ENDPOINTS.dashboardQuotes,
        method: 'GET',
      }),
      keepUnusedDataFor: 120,
    }),
  }),
})

export const { useGetPopularQuotesQuery, useGetDashboardQuotesQuery } = newsApi
