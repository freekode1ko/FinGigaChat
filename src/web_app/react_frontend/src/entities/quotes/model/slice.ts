import { createSlice, type PayloadAction } from '@reduxjs/toolkit'

import type { PopularQuotes } from './types'

type FavoriteQuotesSlice = {
  isShown: boolean
  list: Array<PopularQuotes>
}

const initialState: FavoriteQuotesSlice = {
  isShown: true,
  list: ['FX_IDC:CNYRUB', 'FX_IDC:USDCNY', 'BLACKBULL:BRENT', 'TVC:GOLD'],
}

export const favoriteQuotesSlice = createSlice({
  name: 'favoriteQuotes',
  initialState,
  reducers: {
    toggleFavoriteQuotes: (state) => {
      state.isShown = !state.isShown
    },
    updateFavoriteQuotesList: (
      state,
      action: PayloadAction<Array<PopularQuotes>>
    ) => {
      state.list = action.payload
    },
  },
})

export const selectIsFavoriteQuotesShown = (state: RootState) =>
  state.favoriteQuotes.isShown
export const selectFavoriteQuotesList = (state: RootState) =>
  state.favoriteQuotes.list
export const { toggleFavoriteQuotes, updateFavoriteQuotesList } =
  favoriteQuotesSlice.actions
