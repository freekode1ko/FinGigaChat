import { baseApi } from '@/shared/api'
import { API_ENDPOINTS, KEEP_UNUSED_DATA_TEMP } from '@/shared/model'

import type { Quotes } from '../model'

interface QuotesSection {
  section_name: string
  section_params: Array<string>
  data: Array<Quotes>
}

interface QuotesResponse {
  sections: Array<QuotesSection>
}

const quotesApi = baseApi.injectEndpoints({
  endpoints: (build) => ({
    getPopularQuotes: build.query<QuotesResponse, void>({
      query: () => ({
        url: API_ENDPOINTS.popularQuotes,
        method: 'GET',
      }),
      keepUnusedDataFor: KEEP_UNUSED_DATA_TEMP,
    }),
    getDashboardQuotes: build.query<QuotesResponse, void>({
      query: () => ({
        url: API_ENDPOINTS.dashboardQuotes,
        method: 'GET',
      }),
      keepUnusedDataFor: KEEP_UNUSED_DATA_TEMP,
    }),
  }),
})

export const { useGetPopularQuotesQuery, useGetDashboardQuotesQuery } =
  quotesApi
