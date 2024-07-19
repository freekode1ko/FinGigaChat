import { baseApi, ENDPOINTS } from '@/shared/api'

import type { Quotes } from '../model'

interface QuotesSection {
  section_name: string
  data: Array<Quotes>
}

const newsApi = baseApi.injectEndpoints({
  endpoints: (build) => ({
    getPopularQuotes: build.query<{ sections: Array<QuotesSection> }, void>({
      query: () => ({
        url: ENDPOINTS.popularQuotes,
        method: 'GET',
      }),
      keepUnusedDataFor: 120,
    }),
    getDashboardQuotes: build.query<{ sections: Array<QuotesSection> }, void>({
      query: () => ({
        url: ENDPOINTS.dashboardQuotes,
        method: 'GET',
      }),
      keepUnusedDataFor: 120,
    }),
  }),
})

export const { useGetPopularQuotesQuery, useGetDashboardQuotesQuery } = newsApi
