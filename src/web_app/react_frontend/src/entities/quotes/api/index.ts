import { baseApi } from '@/shared/api'
import { API_ENDPOINTS, API_TAGS, KEEP_UNUSED_DATA_TEMP } from '@/shared/model'

import type { DashboardSubscriptionSection, QuotesSection } from '../model'
import { FinancialData } from '../model/types'

interface QuotesResponse {
  sections: Array<QuotesSection>
}

interface DashboardSubscriptionsResponse {
  subscription_sections: Array<DashboardSubscriptionSection>
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
    getDashboardSubscriptions: build.query<
      DashboardSubscriptionsResponse,
      { userId: number }
    >({
      query: ({ userId }) => ({
        url: `${API_ENDPOINTS.dashboardQuotes}/${userId}/subscriptions`,
        method: 'GET',
      }),
      keepUnusedDataFor: KEEP_UNUSED_DATA_TEMP,
      providesTags: [API_TAGS.dashboard],
    }),
    putDashboardSubscriptions: build.mutation<
      string,
      { userId: number; body: Array<DashboardSubscriptionSection> }
    >({
      query: ({ userId, body }) => ({
        url: `${API_ENDPOINTS.dashboardQuotes}/${userId}/subscriptions`,
        method: 'PUT',
        body: { subscription_sections: body },
      }),
      invalidatesTags: [API_TAGS.dashboard],
    }),
    getDashboardData: build.query<
      { id: number; data: Array<FinancialData> },
      { quoteId: number; startDate: string }
    >({
      query: ({ quoteId, startDate }) => ({
        url: `${API_ENDPOINTS.dashboardQuotes}/data/${quoteId}?start_date=${startDate}`,
        method: 'GET',
      }),
    }),
  }),
})

export const {
  useGetPopularQuotesQuery,
  useGetDashboardQuotesQuery,
  useGetDashboardSubscriptionsQuery,
  usePutDashboardSubscriptionsMutation,
  useGetDashboardDataQuery,
} = quotesApi
