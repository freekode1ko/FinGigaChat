import type { TradingViewSymbol } from './types'

const TRADINGVIEW_QUOTES: Array<TradingViewSymbol> = [
  { name: 'Юань/Рубль (ICE)', id: 'FX_IDC:CNYRUB' },
  { name: 'Доллар/Юань (ICE)', id: 'FX_IDC:USDCNY' },
  { name: 'BRENT (BlackBull)', id: 'BLACKBULL:BRENT' },
  { name: 'Золото (TVC)', id: 'TVC:GOLD' },
  { name: 'Серебро (TVC)', id: 'TVC:SILVER' },
  { name: 'Платина (TVC)', id: 'TVC:PLATINUM' },
  { name: 'Доллар/Рубль (ICE)', id: 'FX_IDC:USDRUB' },
  { name: 'Евро/Рубль (ICE)', id: 'FX_IDC:EURRUB' },
]

const INITIAL_TRADINGVIEW_QUOTES: Array<TradingViewSymbol> =
  TRADINGVIEW_QUOTES.slice(0, 4)

export { INITIAL_TRADINGVIEW_QUOTES, TRADINGVIEW_QUOTES }
