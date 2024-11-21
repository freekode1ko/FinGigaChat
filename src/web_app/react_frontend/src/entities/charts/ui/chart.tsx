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

import type { FinancialData } from '@/entities/quotes'
import { useResizeObserver } from '@/shared/lib'

export const CustomChart = ({
  inputData,
  size,
  height,
  width,
  theme,
}: {
  inputData: Array<FinancialData>
  size: 'small' | 'large'
  height?: number
  width?: number
  theme: Theme
}) => {
  const getOpenCloseColor = () => {
    if (inputData.length < 2) return theme === 'dark' ? '#383E55' : '#E1E1EA'
    let compIndex = inputData.length - 2
    while (inputData[compIndex].date === inputData[inputData.length - 1].date) {
      compIndex -= 1;
    }
    if (!inputData[compIndex]) return theme === 'dark' ? '#383E55' : '#E1E1EA';
    return inputData[inputData.length - 1].value >= inputData[compIndex].value ? "#26A69A" : "#EF5350";
  };

  const openCloseColor = getOpenCloseColor();

  const axisStyles = {
    strokeStyle: theme === 'dark' ? '#383E55' : '#E1E1EA',
    strokeWidth: 2,
    tickLabelFill: theme === 'dark' ? '#9EAAC7' : '#000115',
    tickStrokeStyle: theme === 'dark' ? '#383E55' : '#E1E1EA',
    gridLinesStrokeStyle:
      theme === 'dark' ? 'rgba(56, 62, 85, 0.5)' : 'rgba(245, 245, 234, 0.5)',
  }

  const coordinateStyles = {
    fill: theme === 'dark' ? '#383E55' : '#E1E1EA',
    textFill: theme === 'dark' ? '#FFFFFF' : '#000115',
  }

  const crossHairStyles = {
    strokeStyle: theme === 'dark' ? '#9EAAC7' : '#F4F6F9',
  }

  const zoomButtonStyles = {
    fill: theme === 'dark' ? '#383E55' : '#E1E1EA',
    fillOpacity: 0.75,
    strokeWidth: 0,
    textFill: theme === 'dark' ? '#9EAAC7' : '#F4F6F9',
  }

  const [resetCount, setResetCount] = useState(0)
  const {
    containerRef,
    width: observableWidth,
    height: observableHeight,
  } = useResizeObserver(
    size === 'small'
      ? { initialHeight: height || 60, initialWidth: width || 200 }
      : { initialHeight: height || 150, initialWidth: width || 450 }
  )
  const timeDisplayFormat = timeFormat('%d.%m.%Y')

  const xScaleProvider =
    discontinuousTimeScaleProviderBuilder().inputDateAccessor((d) => d.date)
  const { data, xScale, xAccessor, displayXAccessor } =
    xScaleProvider(inputData)
  const xExtents = [xAccessor(data[0]), xAccessor(data[data.length - 1])]
  return (
    <div ref={containerRef} className="h-full w-full">
      {observableWidth && observableHeight && (
        <ChartCanvas
          height={observableHeight}
          ratio={1.0}
          width={observableWidth}
          seriesName={`Chart ${resetCount}`}
          margin={size == 'small' ?
            { left: 0, right: 0, top: 0, bottom: 0 } 
            : { left: 0, right: 46, top: 0, bottom: 24 }
          }
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
            <LineSeries
              strokeStyle={openCloseColor}
              strokeWidth={2}
              hoverStrokeWidth={3}
              highlightOnHover
              hoverTolerance={50}
              yAccessor={(d) => d.value}
            />
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
              fillStyle="rgb(127,127,127,0.5)"
              fontSize={size === 'large' ? 16 : 12}
              fontWeight="bold"
              text="BRIEF"
              y={observableHeight / 2}
              x={observableWidth / 2}
            />
            {size === 'large' && (
              <>
                <EdgeIndicator
                  itemType="last"
                  rectWidth={48}
                  fill={openCloseColor}
                  lineStroke={openCloseColor}
                  displayFormat={format('.2f')}
                  yAccessor={(d) => d.value}
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
