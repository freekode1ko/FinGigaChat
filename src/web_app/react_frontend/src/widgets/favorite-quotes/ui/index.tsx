import { TradingViewWidget } from '@/shared/ui'

const FavoriteQuotes = () => {
  const TV_DATA = [
    'FX_IDC:CNYRUB',
    'FX_IDC:USDCNY',
    'BLACKBULL:BRENT',
    'TVC:GOLD',
  ]
  return (
    <div className="grid grid-cols-2 gap-4 pb-4">
      {TV_DATA.map((symbol, symbolIdx) => (
        <div key={symbolIdx} className="col-span-1">
          <TradingViewWidget symbol={symbol} />
        </div>
      ))}
    </div>
  )
}

export { FavoriteQuotes }
