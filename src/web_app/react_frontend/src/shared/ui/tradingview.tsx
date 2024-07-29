import { useEffect,useRef } from 'react'

export const TradingViewAdvancedWidget = ({
  symbol,
  autosize,
  width,
  height,
}: {
  symbol: string
  width?: string
  height?: string
  autosize?: boolean
}) => {
  const containerRef = useRef<HTMLDivElement>(null)
  useEffect(
    () => {
      const script = document.createElement("script");
      script.src = "https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js";
      script.type = "text/javascript";
      script.async = true;
      script.innerHTML = JSON.stringify({
          width: width,
          height: height,
          symbol: symbol,
          autosize: autosize,
          interval: "D",
          timezone: "Etc/UTC",
          theme: "dark",
          style: "1",
          locale: "ru",
          allow_symbol_change: false,
          calendar: false,
          support_host: "https://www.tradingview.com"
      })
      if (containerRef.current) {
        containerRef.current.appendChild(script)
      }
    },
    []
  );

  return (
    <div className="tradingview-widget-container" ref={containerRef}>
      <div className="tradingview-widget-container__widget"></div>
    </div>
  );
}

export const TradingViewWidget = ({
    symbol,
    width,
    height,
    autosize = true,
    chartOnly = false,
    noTimeScale = false,
  }: {
    symbol: string
    width?: string
    height?: string
    chartOnly?: boolean
    autosize?: boolean
    noTimeScale?: boolean
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
        colorTheme: 'dark',
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

