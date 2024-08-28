import { createSlice, type PayloadAction } from '@reduxjs/toolkit'

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
  },
})

export const selectUserState = (state: RootState) => state.user
export const selectUserIsAuthenticated = (state: RootState) =>
  state.user.isAuthenticated
export const selectUserData = (state: RootState) => state.user.user
export const { setUser } = userSlice.actions
