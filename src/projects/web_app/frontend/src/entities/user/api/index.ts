import { baseApi } from '@/shared/api'
import {
  API_ENDPOINTS,
  API_TAGS,
  type PaginatedResponse,
  type PaginationProps,
} from '@/shared/model'

import type { User, UserRole } from '../model'

interface UserQuery extends PaginationProps {
  email?: string
  role_id?: number
}

export const usersApi = baseApi.injectEndpoints({
  endpoints: (build) => ({
    getUsers: build.query<PaginatedResponse<User>, UserQuery>({
      query: ({ page, size, email, role_id }) => ({
        url: `${API_ENDPOINTS.users}/`,
        params: { page, size, email, role_id },
        method: 'GET',
      }),
      providesTags: (result) =>
        result
          ? result.items.map(({ email }) => ({
              type: API_TAGS.users,
              email,
            }))
          : [{ type: API_TAGS.users }],
    }),
    getUserRoles: build.query<Array<UserRole>, void>({
      query: () => ({
        url: `${API_ENDPOINTS.users}/roles`,
        method: 'GET',
      }),
    }),
    updateUserRole: build.mutation<string, { roleId: number; email: string }>({
      query: ({ roleId, email }) => ({
        url: `${API_ENDPOINTS.users}/` + email,
        method: 'PATCH',
        body: { role: roleId },
      }),
      invalidatesTags: (_result, _error, { email }) => [
        { type: API_TAGS.users, email },
      ],
    }),
  }),
})

export const {
  useGetUsersQuery,
  useGetUserRolesQuery,
  useUpdateUserRoleMutation,
} = usersApi
