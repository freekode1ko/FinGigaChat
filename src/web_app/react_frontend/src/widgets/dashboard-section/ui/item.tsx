import { useInView } from 'react-intersection-observer'
import { useNavigate } from 'react-router-dom'

import { DashboardSubscriptionUpdateMenu } from '@/features/dashboard/update'
import { ChartSkeleton, CustomChart, mapFinancialData } from '@/entities/charts'
import { QuoteCard, type Quotes,useGetDashboardDataQuery } from '@/entities/quotes'
import { selectAppTheme } from '@/entities/theme'
import { cn, useAppSelector } from '@/shared/lib'
import { SITE_MAP } from '@/shared/model'

interface DashboardItemProps {
  item: Quotes
}

/*
  Компонент карточки с котировкой для дашборда.
*/
const _DashboardItem = ({item}: DashboardItemProps) => {
  const theme = useAppSelector(selectAppTheme)
  const navigate = useNavigate()
  const { data, isLoading } = useGetDashboardDataQuery({
    quoteId: item.quote_id,
    startDate: '01.01.2024', // пока хардкодом забираем данные с начала 2024 года
  })

  if (isLoading)
    return (
      <div className={cn(item.view_type == 1 ? "h-[70px]" : "h-[150px]")}>
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
          size={item.view_type == 1 ? "small" : "large"}
          theme={theme}
        />
      }
      actionSlot={
        <DashboardSubscriptionUpdateMenu
          quoteId={item.quote_id}
          isActive={true}
          viewType={item.view_type}
          instantUpdate={true}
          display="dropdown"
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
const DashboardItemWrapper = ({ item }: DashboardItemProps) => {
  const { ref, inView } = useInView({
    triggerOnce: true,
    rootMargin: '100px',
  })
  return (
    <div ref={ref}>
      {inView && <_DashboardItem item={item} />}
    </div>
  )
}

export { DashboardItemWrapper as DashboardItem }
