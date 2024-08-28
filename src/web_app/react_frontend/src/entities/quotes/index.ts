export { useGetDashboardQuotesQuery, useGetPopularQuotesQuery } from './api'
export {
  favoriteQuotesSlice,
  type Quotes,
  type QuotesSection,
  selectFavoriteQuotesList,
  selectIsFavoriteQuotesShown,
  toggleFavoriteQuotes,
  TRADINGVIEW_QUOTES,
  type TradingViewSymbol,
  updateFavoriteQuotesList,
} from './model'
export { QuotesTable, QuotesTableRow } from './ui'
