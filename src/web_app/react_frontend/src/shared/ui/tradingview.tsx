import { useEffect, useRef } from 'react'

export const TradingViewAdvancedWidget = ({
  symbol,
  autosize,
  width,
  height,
  theme = 'dark',
}: {
  symbol: string
  width?: string
  height?: string
  autosize?: boolean
  theme?: 'dark' | 'light'
}) => {
  const containerRef = useRef<HTMLDivElement>(null)
  useEffect(() => {
    const script = document.createElement('script')
    script.src =
      'https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js'
    script.type = 'text/javascript'
    script.async = true
    script.innerHTML = JSON.stringify({
      width: width,
      height: height,
      symbol: symbol,
      autosize: autosize,
      interval: 'D',
      timezone: 'Etc/UTC',
      theme: theme,
      style: '1',
      locale: 'ru',
      allow_symbol_change: false,
      calendar: false,
      support_host: 'https://www.tradingview.com',
    })
    if (containerRef.current) {
      containerRef.current.appendChild(script)
    }
  }, [])

  return (
    <div className="tradingview-widget-container" ref={containerRef}>
      <div className="tradingview-widget-container__widget"></div>
    </div>
  )
}

export const TradingViewWidget = ({
  symbol,
  width,
  height,
  autosize = true,
  chartOnly = false,
  noTimeScale = false,
  theme = 'dark',
}: {
  symbol: string
  width?: string
  height?: string
  chartOnly?: boolean
  autosize?: boolean
  noTimeScale?: boolean
  theme?: 'dark' | 'light'
}) => {
  const containerRef = useRef<HTMLDivElement>(null)
  useEffect(() => {
    const script = document.createElement('script')
    script.type = 'text/javascript'
    script.async = true
    script.src =
      'https://s3.tradingview.com/external-embedding/embed-widget-mini-symbol-overview.js'
    script.innerHTML = JSON.stringify({
      symbol: symbol,
      autosize: autosize,
      width: width,
      height: height,
      locale: 'ru',
      dateRange: '12M',
      colorTheme: theme,
      isTransparent: false,
      largeChartUrl: '',
      chartOnly: chartOnly,
      noTimeScale: noTimeScale,
    })

    if (containerRef.current) {
      containerRef.current.appendChild(script)
    }
  }, [])

  return (
    <div className="tradingview-widget-container" ref={containerRef}>
      <div className="tradingview-widget-container__widget"></div>
    </div>
  )
}
