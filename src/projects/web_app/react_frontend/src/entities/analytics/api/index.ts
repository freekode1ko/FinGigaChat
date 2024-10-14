import { baseApi } from '@/shared/api'
import {
  API_ENDPOINTS,
  KEEP_UNUSED_DATA_TEMP,
  PaginationProps,
} from '@/shared/model'

import type { Menu, Section } from '../model'

interface GetSectionQuery extends PaginationProps {
  sectionId: string
}

interface GetSectionResponse {
  analytic_id: string
  title: string
  analytics: Array<Section>
}

interface SendAnalyticsQuery {
  userId: number
  reportId: number
}

const analyticsApi = baseApi.injectEndpoints({
  endpoints: (build) => ({
    getMenus: build.query<Menu, void>({
      query: () => ({
        url: API_ENDPOINTS.analytics + '/menu',
        method: 'GET',
      }),
      keepUnusedDataFor: KEEP_UNUSED_DATA_TEMP,
    }),
    getSection: build.query<GetSectionResponse, GetSectionQuery>({
      query: ({ sectionId, page, size }) => ({
        url: `${API_ENDPOINTS.analytics}/section/${sectionId}?page=${page}&size=${size}`,
        method: 'GET',
      }),
      serializeQueryArgs: ({ endpointName }) => {
        return endpointName
      },
      merge: (currentCache, newItems) => {
        currentCache.analytics.push(...newItems.analytics)
      },
      forceRefetch({ currentArg, previousArg }) {
        return currentArg !== previousArg
      },
      keepUnusedDataFor: KEEP_UNUSED_DATA_TEMP,
    }),
    sendAnalytics: build.mutation<string, SendAnalyticsQuery>({
      query: ({ userId, reportId }) => ({
        url: `${API_ENDPOINTS.analytics}/send?user_id=${userId}&report_id=${reportId}`,
        method: 'POST',
      }),
    }),
  }),
})

export const {
  useGetMenusQuery,
  useGetSectionQuery,
  useSendAnalyticsMutation,
} = analyticsApi
