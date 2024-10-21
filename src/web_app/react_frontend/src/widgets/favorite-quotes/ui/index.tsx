import {
  FavoriteQuotesSettings,
  FavoriteQuotesToggler,
} from '@/features/favorite-quotes'
import {
  selectFavoriteQuotesList,
  selectIsFavoriteQuotesShown,
} from '@/entities/quotes'
import { selectAppTheme } from '@/entities/theme'
import { TradingViewMiniChart } from '@/entities/tradingview'
import { useAppSelector } from '@/shared/lib'
import { TypographyH2 } from '@/shared/ui'

const FavoriteQuotes = () => {
  const isFavoriteQuotesShown = useAppSelector(selectIsFavoriteQuotesShown)
  const favoriteQuotes = useAppSelector(selectFavoriteQuotesList)
  const appTheme = useAppSelector(selectAppTheme)

  return (
    <div className="mb-4">
      <div className="flex items-center justify-between mb-2">
        <TypographyH2>Избранные виджеты</TypographyH2>
        <div>
          <FavoriteQuotesToggler />
          <FavoriteQuotesSettings />
        </div>
      </div>
      {isFavoriteQuotesShown && (
        <div className="grid grid-cols-2 gap-4 pb-4">
          {favoriteQuotes.map((symbol) => (
            <div key={symbol.id} className="col-span-1">
              <TradingViewMiniChart
                symbol={symbol.id}
                colorTheme={appTheme}
                autosize
              />
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export { FavoriteQuotes }
