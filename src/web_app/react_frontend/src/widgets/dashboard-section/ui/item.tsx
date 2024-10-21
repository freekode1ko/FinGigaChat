import { useInView } from 'react-intersection-observer'

import type { Quotes } from '@/entities/quotes'

import { LargeChartItem } from './large-chart-item'
import { SmallChartItem } from './small-chart-item'
import { TextItem } from './text-item'

interface DashboardItemProps {
  item: Quotes
}

const DashboardItem = ({ item }: DashboardItemProps) => {
  const { ref, inView } = useInView({
    triggerOnce: true,
    rootMargin: '100px',
  })

  return (
    <div ref={ref}>
      {inView && (
        <>
          {item.view_type === 1 && <TextItem item={item} />}
          {item.view_type === 2 && <SmallChartItem item={item} />}
          {item.view_type === 3 && <LargeChartItem item={item} />}
        </>
      )}
    </div>
  )
}

export { DashboardItem }
