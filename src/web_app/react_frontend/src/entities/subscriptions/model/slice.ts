import { createSlice, PayloadAction } from '@reduxjs/toolkit'

import type { SubscriptionUpdate } from '../model'

interface ManageSubscriptionsSliceState {
  subscriptionsToUpdate: Array<SubscriptionUpdate>
}

const initialState: ManageSubscriptionsSliceState = {
  subscriptionsToUpdate: [],
}

export const manageSubscriptionsSlice = createSlice({
  name: 'manageSubscriptions',
  initialState,
  reducers: {
    setSubscriptions(state, action: PayloadAction<Array<SubscriptionUpdate>>) {
      state.subscriptionsToUpdate = action.payload
    },
    resetSubscriptions(state) {
      state.subscriptionsToUpdate = []
    },
  },
})

export const { setSubscriptions, resetSubscriptions } =
  manageSubscriptionsSlice.actions
export const selectSubscriptionsToUpdate = (state: RootState) =>
  state.manageSubscriptions.subscriptionsToUpdate
