import { Pencil, Search } from 'lucide-react'
import { useEffect, useRef } from 'react'
import { VariableSizeList } from 'react-window'
import { toast } from 'sonner'

import { useDashboardSearch } from '@/features/dashboard/search/lib'
import {
  flattenQuotesContent,
  quotesApi,
  useGetDashboardSubscriptionsQuery,
} from '@/entities/quotes'
import { setSubscriptions } from '@/entities/quotes'
import { selectDashboardSubscriptions } from '@/entities/quotes/model/slice'
import { selectUserData } from '@/entities/user'
import { cn, useAppDispatch, useAppSelector } from '@/shared/lib'
import {
  Button,
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  Input,
} from '@/shared/ui'
import { skipToken } from '@reduxjs/toolkit/query'

import { ItemRow } from './item'

const ManageDashboardButton = () => {
  const listRef = useRef<VariableSizeList>(null)
  const dispatch = useAppDispatch()
  const user = useAppSelector(selectUserData)
  const subscriptions = useAppSelector(selectDashboardSubscriptions)
  const [trigger] =
    quotesApi.endpoints.putDashboardSubscriptionsOnMain.useMutation()
  const { data } = useGetDashboardSubscriptionsQuery(
    user ? { userId: user.id } : skipToken
  )

  useEffect(() => {
    if (data) {
      dispatch(setSubscriptions(data.subscription_sections))
    }
  }, [data, dispatch])

  const handleSave = async () => {
    if (user) {
      toast.promise(
        trigger({ userId: user.id, body: subscriptions }).unwrap(),
        {
          loading: 'Дашборд обновляется...',
          success: 'Дашборд успешно обновлен!',
          error: 'Мы не смогли обновить дашборд. Попробуйте позже.',
        }
      )
    }
  }

  const handleReset = () => {
    if (data) dispatch(setSubscriptions(data.subscription_sections))
  }

  const { searchQuery, setSearchQuery, searchSubscriptions } =
    useDashboardSearch(subscriptions)
  const flattenedContent = flattenQuotesContent(
    searchSubscriptions(searchQuery)
  )

  useEffect(() => {
    if (listRef.current) {
      listRef.current.resetAfterIndex(0, true)
    }
  }, [flattenedContent])

  const getItemSize = (index: number) => {
    const item = flattenedContent[index]
    return item.type === 'section' ? 44 : 56
  }

  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="secondary" size="icon">
          <Pencil />
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>Настроить дашборд</DialogTitle>
          <DialogDescription>
            Выберите, какие котировки отображать на дашборде
          </DialogDescription>
        </DialogHeader>
        <div className="relative">
          <span
            className={cn(
              searchQuery.length > 0 ? 'text-text' : 'text-muted-foreground',
              'absolute inset-y-0 left-3 flex items-center pointer-events-none'
            )}
          >
            <Search />
          </span>
          <Input
            placeholder="Поиск по инструментам и секциям..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-12"
          />
        </div>
        <div className="flex flex-col gap-4 py-2 h-[360px] overflow-y-auto">
          <VariableSizeList
            ref={listRef}
            height={360}
            width="100%"
            itemCount={flattenedContent.length}
            itemSize={getItemSize}
            itemData={flattenedContent}
          >
            {ItemRow}
          </VariableSizeList>
        </div>
        <DialogFooter>
          <DialogClose asChild>
            <Button onClick={handleSave}>Сохранить</Button>
          </DialogClose>
          <Button variant="outline" onClick={handleReset}>
            Отменить
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

export { ManageDashboardButton }
