import { useInView } from 'react-intersection-observer'

import type { DashboardSubscription } from '@/entities/quotes'

import { LargeChartItem } from './large-chart-item'
import { SmallChartItem } from './small-chart-item'
import { TextItem } from './text-item'

interface DashboardItemProps {
  item: DashboardSubscription
}

const DashboardItem = ({ item }: DashboardItemProps) => {
  const { ref, inView } = useInView({
    triggerOnce: true,
    rootMargin: '100px',
  })

  return (
    <div ref={ref} className='break-inside-avoid-column'>
      {inView && (
        <>
          {item.type === 1 && <TextItem item={item} />}
          {item.type === 2 && <SmallChartItem item={item} />}
          {item.type === 3 && <LargeChartItem item={item} />}
        </>
      )}
    </div>
  )
}

export { DashboardItem }
