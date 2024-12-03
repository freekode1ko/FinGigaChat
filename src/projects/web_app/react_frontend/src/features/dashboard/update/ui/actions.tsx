import { EllipsisVertical, RectangleHorizontal, Square, Trash2 } from 'lucide-react'
import { toast } from 'sonner'

import {
  usePutDashboardSubscriptionsMutation,
} from '@/entities/quotes'
import { selectDashboardSubscriptions } from '@/entities/quotes/model/slice'
import { selectUserData } from '@/entities/user'
import { useAppSelector } from '@/shared/lib'
import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/shared/ui'

interface DashboardSubscriptionUpdateMenuProps {
  quoteId: number
  viewType: number
}

const DashboardSubscriptionActions = ({
  quoteId,
  viewType,
  show,
}: DashboardSubscriptionUpdateMenuProps & {show?: boolean}) => {
  // const dispatch = useAppDispatch()
  const subscriptions = useAppSelector(selectDashboardSubscriptions)
  const user = useAppSelector(selectUserData)
  const [trigger] = usePutDashboardSubscriptionsMutation()

  const handleClick = async (
    itemId: number,
    changes: Partial<{ active: boolean; type: number }>
  ) => {
    // FIXME
    const updatedSubscriptions = subscriptions.map((section) => ({
      ...section,
      subscription_items: section.subscription_items.map((sub) =>
        sub.id === itemId ? { ...sub, ...changes } : sub
      ),
    }))
    //

    // dispatch(updateSubscription({ itemId, changes }))
    if (user) {
      toast.promise(
        trigger({ userId: user.id, body: updatedSubscriptions }).unwrap(),
        {
          loading: 'Изменения сохраняются...',
          success: 'Изменения сохранены!',
          error: 'Мы не смогли сохранить изменения. Попробуйте позже.',
        }
      )
    }
  }

  if (!show) return null

  return (
    <DropdownMenu>
      <DropdownMenuTrigger>
        <EllipsisVertical className="h-4 w-4" />
      </DropdownMenuTrigger>
      <DropdownMenuContent className='w-56'>
        <DropdownMenuGroup>
          <DropdownMenuLabel>Тип отображения</DropdownMenuLabel>
          <DropdownMenuCheckboxItem
            checked={viewType === 1}
            onCheckedChange={() => viewType !== 1 && handleClick(quoteId, { type: 1 })}
          >
            <RectangleHorizontal />
            <span>Упрощенный</span>
          </DropdownMenuCheckboxItem>
          <DropdownMenuCheckboxItem
            checked={viewType !== 1}
            onCheckedChange={() => viewType === 1 && handleClick(quoteId, { type: 2 })}
          >
            <Square />
            <span>Расширенный</span>
          </DropdownMenuCheckboxItem>
        </DropdownMenuGroup>
        <DropdownMenuSeparator />
        <DropdownMenuGroup>
          <DropdownMenuItem className='text-destructive' onClick={() => handleClick(quoteId, { active: false })}>
            <Trash2 />
            <span>Скрыть тикер</span>
          </DropdownMenuItem>
        </DropdownMenuGroup>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}

export { DashboardSubscriptionActions }
