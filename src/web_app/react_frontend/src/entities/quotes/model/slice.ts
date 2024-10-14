import { createSlice, PayloadAction } from '@reduxjs/toolkit'

import type { DashboardSubscriptionSection } from '../model'

interface DashboardState {
  subscriptions: Array<DashboardSubscriptionSection>
}

const initialState: DashboardState = {
  subscriptions: [],
}

export const dashboardSubscriptionsSlice = createSlice({
  name: 'dashboardSubscriptions',
  initialState,
  reducers: {
    setSubscriptions(
      state,
      action: PayloadAction<DashboardSubscriptionSection[]>
    ) {
      state.subscriptions = action.payload
    },
    updateSubscription(
      state,
      action: PayloadAction<{
        itemId: number
        changes: Partial<{ active: boolean; type: number }>
      }>
    ) {
      state.subscriptions = state.subscriptions.map((section) => ({
        ...section,
        subscription_items: section.subscription_items.map((item) =>
          item.id === action.payload.itemId
            ? { ...item, ...action.payload.changes }
            : item
        ),
      }))
    },
  },
})

export const selectDashboardSubscriptions = (state: RootState) =>
  state.dashboardSubscriptions.subscriptions
export const { setSubscriptions, updateSubscription } =
  dashboardSubscriptionsSlice.actions
