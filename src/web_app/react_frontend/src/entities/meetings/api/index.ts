import { baseApi } from '@/shared/api'
import { API_ENDPOINTS, KEEP_UNUSED_DATA_TEMP } from '@/shared/model'

interface Meeting {
  theme: string
  date_start: string
}

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
      providesTags: ['meetings'],
    }),
    createMeeting: build.mutation<string, MeetingRequest>({
      query: (meeting) => ({
        url: API_ENDPOINTS.meetings,
        method: 'POST',
        body: meeting,
      }),
      invalidatesTags: ['meetings'],
    }),
  }),
})

export const { useGetMeetingsQuery, useCreateMeetingMutation } = meetingsApi
