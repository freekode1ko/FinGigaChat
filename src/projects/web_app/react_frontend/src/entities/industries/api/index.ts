import { baseApi } from '@/shared/api'
import { API_ENDPOINTS, API_TAGS } from '@/shared/model'

import type { CreateIndustry, CreateIndustryDocument, Industry } from '../model'

const industriesApi = baseApi.injectEndpoints({
  endpoints: (build) => ({
    getIndustries: build.query<Array<Industry>, void>({
      query: () => ({
        url: API_ENDPOINTS.industries + '/',
        method: 'GET',
      }),
      providesTags: [API_TAGS.industries],
    }),
    createIndustry: build.mutation<string, CreateIndustry>({
      query: (body) => ({
        url: `${API_ENDPOINTS.industries}/`,
        method: 'POST',
        body: body,
      }),
      invalidatesTags: [API_TAGS.industries],
    }),
    updateIndustry: build.mutation<
      string,
      { industry: CreateIndustry; id: number }
    >({
      query: ({ industry, id }) => ({
        url: `${API_ENDPOINTS.industries}/` + id,
        method: 'PATCH',
        body: industry,
      }),
      invalidatesTags: [API_TAGS.industries],
    }),
    deleteIndustry: build.mutation<string, { id: number }>({
      query: ({ id }) => ({
        url: `${API_ENDPOINTS.industries}/` + id,
        method: 'DELETE',
      }),
      invalidatesTags: [API_TAGS.industries],
    }),
    uploadIndustryDocument: build.mutation<
      string,
      { document: CreateIndustryDocument; industryId: number }
    >({
      query({ document, industryId }) {
        const formData = new FormData()
        formData.append('file', document.file, document.file.name)
        formData.append('name', document.name)
        return {
          url: `${API_ENDPOINTS.industries}/` + industryId + '/documents',
          method: 'POST',
          body: formData,
        }
      },
    }),
    deleteIndustryDocument: build.mutation<string, { id: number }>({
      query: ({ id }) => ({
        url: `${API_ENDPOINTS.industries}/documents/` + id,
        method: 'DELETE',
      }),
    }),
  }),
})

export const {
  useGetIndustriesQuery,
  useCreateIndustryMutation,
  useDeleteIndustryMutation,
  useUpdateIndustryMutation,
  useUploadIndustryDocumentMutation,
  useDeleteIndustryDocumentMutation,
} = industriesApi
