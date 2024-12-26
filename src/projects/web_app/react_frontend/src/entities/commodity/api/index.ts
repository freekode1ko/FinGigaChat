import { baseApi } from '@/shared/api'
import { API_ENDPOINTS, API_TAGS } from '@/shared/model'

import type { Commodity, CreateCommodityResearch } from '../model'

const commodityApi = baseApi.injectEndpoints({
  endpoints: (build) => ({
    getCommodities: build.query<Array<Commodity>, void>({
      query: () => ({
        url: API_ENDPOINTS.commodities + '/',
        method: 'GET',
      }),
      providesTags: (result) =>
        result
          ? [
              ...result.map(({ id }) => ({
                type: API_TAGS.commodities,
                id,
              })),
              { type: API_TAGS.commodities, id: 'LIST' },
            ]
          : [{ type: API_TAGS.commodities, id: 'LIST' }],
    }),
    uploadCommodityResearch: build.mutation<
      string,
      { research: CreateCommodityResearch; commodityId: number }
    >({
      query({ research, commodityId }) {
        const formData = new FormData()
        if (research.file) formData.append('file', research.file)
        formData.append('text', research.text)
        if (research.title) formData.append('title', research.title)
        return {
          url: `${API_ENDPOINTS.commodities}/` + commodityId + '/researches',
          method: 'POST',
          body: formData,
        }
      },
      invalidatesTags: (_result, _error, { commodityId }) => [
        { type: API_TAGS.commodities, id: commodityId },
        { type: API_TAGS.commodities, id: 'LIST' },
      ],
    }),
  }),
})

export const { useGetCommoditiesQuery, useUploadCommodityResearchMutation } =
  commodityApi
