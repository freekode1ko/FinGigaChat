import { format } from 'd3-format'
import { timeFormat } from 'd3-time-format'
import { useState } from 'react'
import {
  Chart,
  ChartCanvas,
  CrossHairCursor,
  discontinuousTimeScaleProviderBuilder,
  Label,
  LineSeries,
  MouseCoordinateX,
  MouseCoordinateY,
  XAxis,
  YAxis,
  ZoomButtons,
} from 'react-financial-charts'

import { FinancialData } from '@/entities/quotes/model/types'
import { useResizeObserver } from '@/shared/lib'

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

export const ChartDemo = ({
  inputData,
  symbol,
}: {
  inputData: Array<FinancialData>
  symbol: string
}) => {
  const [resetCount, setResetCount] = useState(0)
  const { containerRef, width, height } = useResizeObserver()
  const timeDisplayFormat = timeFormat('%d.%m.%Y')

  const xScaleProvider =
    discontinuousTimeScaleProviderBuilder().inputDateAccessor((d) => d.date)
  const { data, xScale, xAccessor, displayXAccessor } =
    xScaleProvider(inputData)
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
          <Chart
            id={1}
            yExtents={(d) => [
              d.value - d.value * 0.02,
              d.value + d.value * 0.02,
            ]}
          >
            <Label
              x={width / 4}
              y={height / 2}
              fontSize={9}
              fillStyle="#bebbbb"
              fontWeight="bold"
              text={symbol}
            />
            <LineSeries yAccessor={(d) => d.value} />
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
