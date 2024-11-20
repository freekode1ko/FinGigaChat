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

export const quotesApi = baseApi.injectEndpoints({
  endpoints: (build) => ({
    getDashboardQuotes: build.query<QuotesResponse, void>({
      query: () => ({
        url: `${API_ENDPOINTS.dashboardQuotes}/`,
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
      providesTags: [API_TAGS.dashboardSubscriptions],
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
      invalidatesTags: [
        API_TAGS.dashboardSubscriptions,
        API_TAGS.dashboardQuotes,
      ],
    }),
    putDashboardSubscriptionsOnMain: build.mutation<
      string,
      { userId: number; body: Array<DashboardSubscriptionSection> }
    >({
      query: ({ userId, body }) => ({
        url: `${API_ENDPOINTS.dashboardQuotes}/${userId}/subscriptions`,
        method: 'PUT',
        body: { subscription_sections: body },
      }),
      invalidatesTags: [
        API_TAGS.dashboardSubscriptions,
        API_TAGS.dashboardQuotes,
      ],
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
    getUserDashboard: build.query<QuotesResponse, { userId: number }>({
      query: ({ userId }) => ({
        url: `${API_ENDPOINTS.dashboardQuotes}/${userId}`,
        method: 'GET',
      }),
      transformResponse: (response: QuotesResponse) => {
        // порядок секций с бэка не гарантируется
        return {
          ...response,
          sections: response.sections.sort((a, b) =>
            a.section_name.localeCompare(b.section_name)
          ),
        }
      },
      providesTags: [API_TAGS.dashboardQuotes],
    }),
  }),
})

export const {
  useGetDashboardQuotesQuery,
  useGetDashboardSubscriptionsQuery,
  usePutDashboardSubscriptionsMutation,
  useGetDashboardDataQuery,
  useGetUserDashboardQuery,
} = quotesApi
