import { createSlice, type PayloadAction } from '@reduxjs/toolkit'

import { authApi } from '../api'
import { User } from './types'

type UserSliceState = {
  isAuthenticated: boolean
  user: Optional<User>
}

const initialState: UserSliceState = {
  isAuthenticated: false,
  user: null,
}

export const userSlice = createSlice({
  name: 'user',
  initialState,
  reducers: {
    setUser: (state, action: PayloadAction<User>) => {
      state.isAuthenticated = true
      state.user = action.payload
    },
    unsetUser: (state) => {
      state.isAuthenticated = false
      state.user = null
    },
  },
  extraReducers: (builder) => {
    builder.addMatcher(
      authApi.endpoints.getCurrentUser.matchFulfilled,
      (state, { payload }) => {
        state.isAuthenticated = true
        state.user = payload
      }
    )
  },
})

export const selectUserIsAuthenticated = (state: RootState) =>
  state.user.isAuthenticated
export const selectUserData = (state: RootState) => state.user.user
export const { setUser, unsetUser } = userSlice.actions
