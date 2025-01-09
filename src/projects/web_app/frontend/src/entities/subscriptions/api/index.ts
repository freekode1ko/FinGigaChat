import { baseApi } from '@/shared/api'
import { API_ENDPOINTS, KEEP_UNUSED_DATA_TEMP } from '@/shared/model'

import type { Subscription } from '../model'
import { SubscriptionUpdate } from '../model/types'

interface SubscriptionRequest {
  userId: number
  body: Array<SubscriptionUpdate>
}

const analyticsApi = baseApi.injectEndpoints({
  endpoints: (build) => ({
    getSubscriptions: build.query<Subscription, { userId: number }>({
      query: ({ userId }) => ({
        url: API_ENDPOINTS.subscriptions + `/${userId}`,
        method: 'GET',
      }),
      keepUnusedDataFor: KEEP_UNUSED_DATA_TEMP,
    }),
    updateSubscriptions: build.mutation<string, SubscriptionRequest>({
      query: (subscription) => ({
        url: API_ENDPOINTS.subscriptions + `/${subscription.userId}`,
        method: 'PUT',
        body: subscription.body,
      }),
    }),
  }),
})

export const { useGetSubscriptionsQuery, useUpdateSubscriptionsMutation } =
  analyticsApi
