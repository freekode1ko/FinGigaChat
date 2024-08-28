import { createSlice, type PayloadAction } from '@reduxjs/toolkit'

import { INITIAL_TRADINGVIEW_QUOTES } from './constants'
import type { TradingViewSymbol } from './types'

type FavoriteQuotesSlice = {
  isShown: boolean
  list: Array<TradingViewSymbol>
}

const initialState: FavoriteQuotesSlice = {
  isShown: true,
  list: INITIAL_TRADINGVIEW_QUOTES,
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
      action: PayloadAction<Array<TradingViewSymbol>>
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
