import { format } from 'd3-format'
import { timeFormat } from 'd3-time-format'
import { useState } from 'react'
import {
  Chart,
  ChartCanvas,
  CrossHairCursor,
  discontinuousTimeScaleProviderBuilder,
  EdgeIndicator,
  Label,
  lastVisibleItemBasedZoomAnchor,
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
const coordinateStyles = {
  fill: '#383E55',
  textFill: '#FFFFFF',
}

const crossHairStyles = {
  strokeStyle: '#9EAAC7',
}

const zoomButtonStyles = {
  fill: '#383E55',
  fillOpacity: 0.75,
  strokeWidth: 0,
  textFill: '#9EAAC7',
}

export const ChartDemo = ({
  inputData,
  size,
  maxHeight,
}: {
  inputData: Array<FinancialData>
  size: 'small' | 'large'
  maxHeight?: number
}) => {
  const [resetCount, setResetCount] = useState(0)
  const { containerRef, width, height } = useResizeObserver(
    size === 'small'
      ? { initialHeight: maxHeight || 150 }
      : { initialHeight: maxHeight || 250 }
  )
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
          zoomAnchor={lastVisibleItemBasedZoomAnchor}
        >
          <Chart
            id={1}
            yExtents={(d) => [
              d.value - d.value * 0.02,
              d.value + d.value * 0.02,
            ]}
          >
            {size === 'large' && (
              <>
                <EdgeIndicator
                  itemType="last"
                  rectWidth={48}
                  fill="#7f7f7f"
                  lineStroke="#7f7f7f"
                  displayFormat={format('.2f')}
                  yAccessor={(d) => d.value}
                />
                <ZoomButtons
                  onReset={() => setResetCount(resetCount + 1)}
                  {...zoomButtonStyles}
                />
              </>
            )}
            <LineSeries yAccessor={(d) => d.value} />
            <XAxis {...axisStyles} showGridLines={size === 'large'} />
            <MouseCoordinateX
              displayFormat={timeDisplayFormat}
              {...coordinateStyles}
            />
            <YAxis {...axisStyles} showGridLines={size === 'large'} />
            <MouseCoordinateY
              displayFormat={format('.2f')}
              {...coordinateStyles}
            />
            <Label
              fillStyle="#7f7f7f"
              fontSize={size === 'large' ? 16 : 12}
              fontWeight="bold"
              text="BRIEF"
              y={height / 2}
              x={width / 2}
            />
          </Chart>
          <CrossHairCursor {...crossHairStyles} />
        </ChartCanvas>
      )}
    </div>
  )
}
