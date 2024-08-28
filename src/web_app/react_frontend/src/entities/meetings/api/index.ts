import { baseApi } from '@/shared/api'
import {
  API_ENDPOINTS,
  KEEP_UNUSED_DATA_TEMP,
  MEETINGS_API_TAG,
} from '@/shared/model'

import type { Meeting } from '../model'

interface MeetingRequest {
  user_id: number
  theme: string
  date_start: string
  date_end: string
  description: string
  timezone: number
}

const meetingsApi = baseApi.injectEndpoints({
  endpoints: (build) => ({
    getMeetings: build.query<Array<Meeting>, { userId: number }>({
      query: ({ userId }) => ({
        url: `${API_ENDPOINTS.meetings}/${userId}`,
        method: 'GET',
      }),
      keepUnusedDataFor: KEEP_UNUSED_DATA_TEMP,
      providesTags: [MEETINGS_API_TAG],
    }),
    createMeeting: build.mutation<string, MeetingRequest>({
      query: (meeting) => ({
        url: API_ENDPOINTS.meetings,
        method: 'POST',
        body: meeting,
      }),
      invalidatesTags: [MEETINGS_API_TAG],
    }),
  }),
})

export const { useGetMeetingsQuery, useCreateMeetingMutation } = meetingsApi
