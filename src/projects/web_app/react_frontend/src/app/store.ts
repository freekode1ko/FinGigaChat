import { dashboardSubscriptionsSlice } from '@/entities/quotes'
import { manageSubscriptionsSlice } from '@/entities/subscriptions'
import { themeSlice } from '@/entities/theme'
import { userSlice } from '@/entities/auth'
import { baseApi } from '@/shared/api'
import { loadFromLocalStorage, saveToLocalStorage } from '@/shared/lib/redux'
import { configureStore } from '@reduxjs/toolkit'

const preloadedState = {
  [themeSlice.name]: loadFromLocalStorage(themeSlice.name),
}

export const store = configureStore({
  // devTools: import.meta.env.VITE_DEBUG === 'true',
  reducer: {
    [baseApi.reducerPath]: baseApi.reducer,
    [userSlice.name]: userSlice.reducer,
    [themeSlice.name]: themeSlice.reducer,
    [manageSubscriptionsSlice.name]: manageSubscriptionsSlice.reducer,
    [dashboardSubscriptionsSlice.name]: dashboardSubscriptionsSlice.reducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware().concat(baseApi.middleware),
  preloadedState,
})

store.subscribe(() => {
  saveToLocalStorage(themeSlice.name, store.getState()[themeSlice.name])
})

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch
