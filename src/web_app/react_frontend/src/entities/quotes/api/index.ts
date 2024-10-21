import { toast } from 'sonner'

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
    getPopularQuotes: build.query<QuotesResponse, void>({
      query: () => ({
        url: `${API_ENDPOINTS.popularQuotes}/`,
        method: 'GET',
      }),
      keepUnusedDataFor: KEEP_UNUSED_DATA_TEMP,
    }),
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
      async onQueryStarted({ userId, body }, { dispatch, queryFulfilled }) {
        const patchResult = dispatch(
          quotesApi.util.updateQueryData(
            'getUserDashboard',
            { userId },
            (draft) => {
              body.forEach((subscriptionSection) => {
                const quoteSection = draft.sections.find(
                  (section) =>
                    section.section_name === subscriptionSection.section_name
                )
                if (quoteSection) {
                  subscriptionSection.subscription_items.forEach(
                    (subscription) => {
                      const quoteIndex = quoteSection.data.findIndex(
                        (quote) => quote.ticker === subscription.ticker
                      )
                      if (quoteIndex !== -1) {
                        const quote = quoteSection.data[quoteIndex]
                        if (!subscription.active) {
                          quoteSection.data.splice(quoteIndex, 1)
                        } else {
                          if (quote.view_type !== subscription.type) {
                            quote.view_type = subscription.type
                          }
                        }
                      }
                    }
                  )
                }
              })
            }
          )
        )
        try {
          await queryFulfilled
          toast.success('Подписки успешно обновлены!')
        } catch {
          patchResult.undo()
          toast.error('Мы не смогли обновить подписки. Попробуйте позже.')
        }
      },
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
    invalidatesTags: [API_TAGS.dashboardQuotes],
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
      providesTags: [API_TAGS.dashboardQuotes]
    }),
  }),
})

export const {
  useGetPopularQuotesQuery,
  useGetDashboardQuotesQuery,
  useGetDashboardSubscriptionsQuery,
  usePutDashboardSubscriptionsMutation,
  useGetDashboardDataQuery,
  useGetUserDashboardQuery,
} = quotesApi
