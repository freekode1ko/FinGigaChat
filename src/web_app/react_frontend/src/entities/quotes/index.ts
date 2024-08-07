export { useGetDashboardQuotesQuery, useGetPopularQuotesQuery } from './api'
export {
  favoriteQuotesSlice,
  POPULAR_QUOTES,
  type PopularQuotes,
  type Quotes,
  selectFavoriteQuotesList,
  selectIsFavoriteQuotesShown,
  toggleFavoriteQuotes,
  updateFavoriteQuotesList,
} from './model'
export { QuotesTable } from './ui'
