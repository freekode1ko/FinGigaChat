import { format } from 'd3-format'
import { timeFormat } from 'd3-time-format'
import { useState } from 'react'
import {
  CandlestickSeries,
  Chart,
  ChartCanvas,
  CrossHairCursor,
  discontinuousTimeScaleProviderBuilder,
  Label,
  MouseCoordinateX,
  MouseCoordinateY,
  OHLCTooltip,
  XAxis,
  YAxis,
  ZoomButtons,
} from 'react-financial-charts'

import { useResizeObserver } from '@/shared/lib'

const DATA = [
  {
    date: '2024-09-06 11:33:47',
    open: 100.0,
    high: 104.63,
    low: 99.07,
    close: 103.12,
    volume: 880,
  },
  {
    date: '2024-09-06 11:34:47',
    open: 103.12,
    high: 106.7,
    low: 101.89,
    close: 106.38,
    volume: 1127,
  },
  {
    date: '2024-09-06 11:35:47',
    open: 106.38,
    high: 107.17,
    low: 103.49,
    close: 106.33,
    volume: 1013,
  },
  {
    date: '2024-09-06 11:36:47',
    open: 106.33,
    high: 110.31,
    low: 105.92,
    close: 107.9,
    volume: 1018,
  },
  {
    date: '2024-09-06 11:37:47',
    open: 107.9,
    high: 109.18,
    low: 106.01,
    close: 108.69,
    volume: 841,
  },
  {
    date: '2024-09-06 11:38:47',
    open: 108.69,
    high: 109.02,
    low: 103.81,
    close: 106.99,
    volume: 830,
  },
  {
    date: '2024-09-06 11:39:47',
    open: 106.99,
    high: 111.23,
    low: 106.08,
    close: 110.79,
    volume: 809,
  },
  {
    date: '2024-09-06 11:40:47',
    open: 110.79,
    high: 111.25,
    low: 107.65,
    close: 107.65,
    volume: 975,
  },
  {
    date: '2024-09-06 11:41:47',
    open: 107.65,
    high: 111.65,
    low: 105.08,
    close: 107.12,
    volume: 1130,
  },
  {
    date: '2024-09-06 11:42:47',
    open: 107.12,
    high: 107.91,
    low: 102.36,
    close: 105.14,
    volume: 1116,
  },
  {
    date: '2024-09-06 11:43:47',
    open: 105.14,
    high: 110.08,
    low: 104.32,
    close: 104.8,
    volume: 972,
  },
  {
    date: '2024-09-06 11:44:47',
    open: 104.8,
    high: 108.06,
    low: 103.95,
    close: 107.87,
    volume: 936,
  },
  {
    date: '2024-09-06 11:45:47',
    open: 107.87,
    high: 109.34,
    low: 104.67,
    close: 105.32,
    volume: 849,
  },
  {
    date: '2024-09-06 11:46:47',
    open: 105.32,
    high: 109.72,
    low: 103.69,
    close: 107.14,
    volume: 973,
  },
  {
    date: '2024-09-06 11:47:47',
    open: 107.14,
    high: 110.89,
    low: 104.67,
    close: 110.57,
    volume: 990,
  },
  {
    date: '2024-09-06 11:48:47',
    open: 110.57,
    high: 114.04,
    low: 108.42,
    close: 113.97,
    volume: 1052,
  },
  {
    date: '2024-09-06 11:49:47',
    open: 113.97,
    high: 115.44,
    low: 112.12,
    close: 114.37,
    volume: 934,
  },
  {
    date: '2024-09-06 11:50:47',
    open: 114.37,
    high: 116.42,
    low: 112.31,
    close: 114.67,
    volume: 888,
  },
  {
    date: '2024-09-06 11:51:47',
    open: 114.67,
    high: 118.23,
    low: 113.34,
    close: 117.08,
    volume: 836,
  },
  {
    date: '2024-09-06 11:52:47',
    open: 117.08,
    high: 120.03,
    low: 116.63,
    close: 117.67,
    volume: 865,
  },
  {
    date: '2024-09-06 11:53:47',
    open: 117.67,
    high: 121.97,
    low: 115.49,
    close: 119.48,
    volume: 1025,
  },
  {
    date: '2024-09-06 11:54:47',
    open: 119.48,
    high: 120.89,
    low: 117.22,
    close: 117.9,
    volume: 925,
  },
  {
    date: '2024-09-06 11:55:47',
    open: 117.9,
    high: 122.36,
    low: 114.77,
    close: 120.67,
    volume: 830,
  },
  {
    date: '2024-09-06 11:56:47',
    open: 120.67,
    high: 122.86,
    low: 118.76,
    close: 121.99,
    volume: 1017,
  },
  {
    date: '2024-09-06 11:57:47',
    open: 121.99,
    high: 126.68,
    low: 121.29,
    close: 125.47,
    volume: 988,
  },
  {
    date: '2024-09-06 11:58:47',
    open: 125.47,
    high: 127.04,
    low: 124.79,
    close: 126.12,
    volume: 1180,
  },
  {
    date: '2024-09-06 11:59:47',
    open: 126.12,
    high: 127.79,
    low: 121.23,
    close: 127.15,
    volume: 1005,
  },
  {
    date: '2024-09-06 12:00:47',
    open: 127.15,
    high: 128.56,
    low: 123.07,
    close: 123.6,
    volume: 1126,
  },
  {
    date: '2024-09-06 12:01:47',
    open: 123.6,
    high: 125.29,
    low: 118.66,
    close: 124.48,
    volume: 881,
  },
  {
    date: '2024-09-06 12:02:47',
    open: 124.48,
    high: 125.33,
    low: 119.88,
    close: 124.0,
    volume: 802,
  },
]

const axisStyles = {
  strokeStyle: '#383E55',
  strokeWidth: 2,
  tickLabelFill: '#9EAAC7',
  tickStrokeStyle: '#383E55',
  gridLinesStrokeStyle: 'rgba(56, 62, 85, 0.5)',
}

const zoomButtonStyles = {
  fill: '#383E55',
  fillOpacity: 0.75,
  strokeWidth: 0,
  textFill: '#9EAAC7',
}

const coordinateStyles = {
  fill: '#383E55',
  textFill: '#FFFFFF',
}

const crossHairStyles = {
  strokeStyle: '#9EAAC7',
}

const parsedData = DATA.map((item) => ({
  ...item,
  date: new Date(item.date),
}))

export const ChartDemo = ({ symbol }: { symbol: string }) => {
  const [resetCount, setResetCount] = useState(0)
  const { containerRef, width, height } = useResizeObserver()
  const timeDisplayFormat = timeFormat('%d.%m.%y \xa0 %H:%M')

  const xScaleProvider =
    discontinuousTimeScaleProviderBuilder().inputDateAccessor((d) => d.date)
  const { data, xScale, xAccessor, displayXAccessor } =
    xScaleProvider(parsedData)
  const xExtents = [xAccessor(data[0]), xAccessor(data[data.length - 1])]
  return (
    <div ref={containerRef} className="h-full w-full">
      {width && height && (
        <ChartCanvas
          height={height}
          ratio={1.2}
          width={width}
          seriesName={`Chart ${resetCount}`}
          margin={{ left: 0, right: 48, top: 0, bottom: 24 }}
          data={data}
          xScale={xScale}
          xAccessor={xAccessor}
          displayXAccessor={displayXAccessor}
          xExtents={xExtents}
        >
          <Chart id="c" yExtents={(d) => [d.high, d.low]}>
            <Label
              x={width * 0.6}
              y={height * 0.8}
              fontSize={16}
              text={symbol}
            />
            <CandlestickSeries />
            <XAxis {...axisStyles} showGridLines />
            <MouseCoordinateX
              displayFormat={timeDisplayFormat}
              {...coordinateStyles}
            />
            <YAxis {...axisStyles} showGridLines />
            <MouseCoordinateY
              displayFormat={format('.2f')}
              {...coordinateStyles}
            />
            {width > 200 && height > 150 && (
              <>
                <OHLCTooltip
                  fontSize={12}
                  textFill="#CBD5E0"
                  origin={[8, 16]}
                />
                <ZoomButtons
                  onReset={() => setResetCount(resetCount + 1)}
                  {...zoomButtonStyles}
                />
              </>
            )}
          </Chart>
          <CrossHairCursor {...crossHairStyles} />
        </ChartCanvas>
      )}
    </div>
  )
}
