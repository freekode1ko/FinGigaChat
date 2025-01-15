import { useInView } from 'react-intersection-observer'
import { useNavigate } from 'react-router-dom'

import { DashboardSubscriptionActions } from '@/features/dashboard/update'
import { ChartSkeleton, CustomChart, mapFinancialData } from '@/entities/charts'
import {
  QuoteCard,
  type Quotes,
  useGetDashboardDataQuery,
} from '@/entities/quotes'
import { selectAppTheme } from '@/entities/theme'
import { cn, useAppSelector } from '@/shared/lib'
import { GRAPH_POLLING_INTERVAL, SITE_MAP } from '@/shared/model'

interface DashboardItemProps {
  item: Quotes
  allowEdit: boolean
}

/*
  Компонент карточки с котировкой для дашборда.
*/
const _DashboardItem = ({ item, allowEdit }: DashboardItemProps) => {
  const theme = useAppSelector(selectAppTheme)
  const navigate = useNavigate()
  const { data, isLoading } = useGetDashboardDataQuery(
    {
      quoteId: item.quote_id,
      startDate: '01.01.2024', // пока хардкодом забираем данные с начала 2024 года
    },
    {
      pollingInterval: GRAPH_POLLING_INTERVAL,
      skipPollingIfUnfocused: true,
    }
  )

  if (isLoading)
    return (
      <div className={cn(item.view_type == 1 ? 'h-[70px]' : 'h-[150px]')}>
        <ChartSkeleton />
      </div>
    )

  if (!data || data?.data.length < 2)
    return (
      <QuoteCard
        name={item.name}
        value={item.value}
        params={item.params}
        type={1}
        ticker={item.ticker}
        onCardClick={() =>
          navigate(`${SITE_MAP.dashboard}/quote/${item.quote_id}`)
        }
        actionSlot={
          <DashboardSubscriptionActions
            quoteId={item.quote_id}
            viewType={item.view_type}
            show={allowEdit}
          />
        }
      />
    )

  return (
    <QuoteCard
      name={item.name}
      value={item.value}
      params={item.params}
      type={item.view_type}
      ticker={item.ticker}
      onCardClick={() =>
        navigate(`${SITE_MAP.dashboard}/quote/${item.quote_id}`)
      }
      graph={
        <CustomChart
          inputData={mapFinancialData([...data.data].reverse())}
          size={item.view_type == 1 ? 'small' : 'large'}
          theme={theme}
        />
      }
      actionSlot={
        <DashboardSubscriptionActions
          quoteId={item.quote_id}
          viewType={item.view_type}
          show={allowEdit}
        />
      }
    />
  )
}

/*
  Обертка для умного рендеринга компонента: загружаем данные только в том случае,
  если он попал на экран пользователя. Это полезно на мобильных устройствах, когда
  на экран попадают лишь несколько карточек. Чтобы сразу не загружать все содержимое
  дашборда, оно будет подгружаться динамически, когда пользователь доскроллит до
  нужного места.
*/
const DashboardItemWrapper = (props: DashboardItemProps) => {
  const { ref, inView } = useInView({
    triggerOnce: true,
    rootMargin: '100px',
  })
  return <div ref={ref}>{inView && <_DashboardItem {...props} />}</div>
}

export { DashboardItemWrapper as DashboardItem }
