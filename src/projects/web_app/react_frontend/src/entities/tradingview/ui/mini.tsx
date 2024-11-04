import { memo } from 'react'

import { Widget } from './widget'

export type MiniChartProps = {
  symbol?: string
  width?: number | string
  height?: number | string
  colorTheme?: Theme
  trendLineColor?: string
  underLineColor?: string
  underLineBottomColor?: string
  isTransparent?: boolean
  autosize?: boolean
  largeChartUrl?: string
  chartOnly?: boolean
  noTimeScale?: boolean
  children?: never
}

const MiniChartComponent = ({
  symbol = 'FX:EURUSD',
  width = 350,
  height = 220,
  colorTheme = 'light',
  trendLineColor = 'rgba(41, 98, 255, 1)',
  underLineColor = 'rgba(41, 98, 255, 0.3)',
  underLineBottomColor = 'rgba(41, 98, 255, 0)',
  isTransparent = false,
  autosize = false,
  largeChartUrl = undefined,
  chartOnly = false,
  noTimeScale = false,
  ...props
}: MiniChartProps) => {
  return (
    <Widget
      scriptHTML={{
        symbol,
        ...(!autosize ? { width } : { width: '100%' }),
        ...(!autosize ? { height } : { height: '100%' }),
        colorTheme,
        trendLineColor,
        underLineColor,
        underLineBottomColor,
        isTransparent,
        autosize,
        largeChartUrl,
        chartOnly,
        noTimeScale,
        ...props,
      }}
      scriptSRC="https://s3.tradingview.com/external-embedding/embed-widget-mini-symbol-overview.js"
    />
  )
}

export const MiniChart = memo(MiniChartComponent)
