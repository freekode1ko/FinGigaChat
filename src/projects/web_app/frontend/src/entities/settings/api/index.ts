import { baseApi } from '@/shared/api'
import { API_ENDPOINTS, API_TAGS } from '@/shared/model'

import type { Setting } from '../model'

const settingsApi = baseApi.injectEndpoints({
  endpoints: (build) => ({
    getSettings: build.query<Array<Setting>, void>({
      query: () => ({
        url: API_ENDPOINTS.settings + '/',
        method: 'GET',
      }),
      keepUnusedDataFor: 300,
      providesTags: (result) =>
        result
          ? [
              ...result.map(({ key }) => ({
                type: API_TAGS.settings,
                id: key,
              })),
              { type: API_TAGS.settings, id: 'LIST' },
            ]
          : [{ type: API_TAGS.settings, id: 'LIST' }],
    }),
    setSetting: build.mutation<void, { newValue: string; key: string }>({
      query: ({ key, newValue }) => ({
        url: API_ENDPOINTS.settings + `/${key}`,
        method: 'POST',
        body: { value: newValue },
      }),
      invalidatesTags: (_result, _error, { key }) => [
        { type: API_TAGS.settings, id: key },
        { type: API_TAGS.settings, id: 'LIST' },
      ],
    }),
  }),
})

export const { useGetSettingsQuery, useSetSettingMutation } = settingsApi
