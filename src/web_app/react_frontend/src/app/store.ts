import { favoriteQuotesSlice } from '@/entities/quotes'
import { manageSubscriptionsSlice } from '@/entities/subscriptions'
import { themeSlice } from '@/entities/theme'
import { userSlice } from '@/entities/user'
import { baseApi } from '@/shared/api'
import { loadFromLocalStorage, saveToLocalStorage } from '@/shared/lib/redux'
import { configureStore } from '@reduxjs/toolkit'

const preloadedState = {
  [favoriteQuotesSlice.name]: loadFromLocalStorage(favoriteQuotesSlice.name),
}

export const store = configureStore({
  // devTools: import.meta.env.VITE_DEBUG === 'true',
  reducer: {
    [baseApi.reducerPath]: baseApi.reducer,
    [userSlice.name]: userSlice.reducer,
    [themeSlice.name]: themeSlice.reducer,
    [manageSubscriptionsSlice.name]: manageSubscriptionsSlice.reducer,
    [favoriteQuotesSlice.name]: favoriteQuotesSlice.reducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware().concat(baseApi.middleware),
  preloadedState,
})

store.subscribe(() => {
  saveToLocalStorage(
    favoriteQuotesSlice.name,
    store.getState()[favoriteQuotesSlice.name]
  )
})

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch
