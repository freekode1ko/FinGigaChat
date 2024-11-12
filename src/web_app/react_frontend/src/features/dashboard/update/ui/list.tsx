import { ArrowDown, Eye, EyeOff, Grid2X2, ListIcon, Square } from 'lucide-react'
import { toast } from 'sonner'

import {
  updateSubscription,
  usePutDashboardSubscriptionsMutation,
} from '@/entities/quotes'
import { selectDashboardSubscriptions } from '@/entities/quotes/model/slice'
import { selectUserData } from '@/entities/user'
import { useAppDispatch, useAppSelector } from '@/shared/lib'
import {
  Button,
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuTrigger,
} from '@/shared/ui'

interface DashboardSubscriptionUpdateMenuProps {
  quoteId: number
  isActive: boolean
  viewType: number
  instantUpdate?: boolean
  display?: 'row' | 'dropdown'
}

const DashboardSubscriptionUpdateMenu = ({
  quoteId,
  isActive,
  viewType,
  instantUpdate,
  display = 'row',
}: DashboardSubscriptionUpdateMenuProps) => {
  const dispatch = useAppDispatch()
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

    dispatch(updateSubscription({ itemId, changes }))
    if (instantUpdate && user) {
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

  const renderButtons = () => (
    <div className="flex space-x-2">
      <Button
        variant="ghost"
        size="icon"
        onClick={() => handleClick(quoteId, { active: !isActive })}
      >
        {isActive ? (
          <Eye className="w-5 h-5" />
        ) : (
          <EyeOff className="w-5 h-5" />
        )}
      </Button>
      <Button
        variant={viewType === 1 ? 'secondary' : 'ghost'}
        size="icon"
        disabled={!isActive}
        onClick={() => handleClick(quoteId, { type: 1 })}
      >
        <ListIcon className="w-5 h-5" />
      </Button>
      <Button
        variant={viewType === 2 ? 'secondary' : 'ghost'}
        size="icon"
        disabled={!isActive}
        onClick={() => handleClick(quoteId, { type: 2 })}
      >
        <Grid2X2 className="w-5 h-5" />
      </Button>
      <Button
        variant={viewType === 3 ? 'secondary' : 'ghost'}
        size="icon"
        disabled={!isActive}
        onClick={() => handleClick(quoteId, { type: 3 })}
      >
        <Square className="w-5 h-5" />
      </Button>
    </div>
  )

  if (display === 'row') return renderButtons()
  return (
    <DropdownMenu>
      <DropdownMenuTrigger>
        <ArrowDown className="h-4 w-4" />
      </DropdownMenuTrigger>
      <DropdownMenuContent>{renderButtons()}</DropdownMenuContent>
    </DropdownMenu>
  )
}

export { DashboardSubscriptionUpdateMenu }
