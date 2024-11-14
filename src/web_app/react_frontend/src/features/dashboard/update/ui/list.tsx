import { RectangleHorizontal, Square } from 'lucide-react'
import { useId } from 'react'

import {
  updateSubscription,
} from '@/entities/quotes'
import { cn, useAppDispatch } from '@/shared/lib'
import {
  Button,
  Checkbox,
  Label,
} from '@/shared/ui'

interface DashboardSubscriptionUpdateMenuProps {
  quoteId: number
  quoteName: string
  isActive: boolean
  viewType: number
  instantUpdate?: boolean
  display?: 'row' | 'dropdown'
}

const DashboardSubscriptionUpdateMenu = ({
  quoteId,
  quoteName,
  isActive,
  viewType,
}: DashboardSubscriptionUpdateMenuProps) => {
  const dispatch = useAppDispatch()
  const hintId = useId()

  const handleClick = (
    itemId: number,
    changes: Partial<{ active: boolean; type: number }>
  ) => dispatch(updateSubscription({ itemId, changes }))

  return (
    <div className="flex items-center justify-between gap-2 py-2">
      <div className='flex flex-row flex-[2] items-center gap-2'>
        <Checkbox id={hintId} checked={isActive} onCheckedChange={() => handleClick(quoteId, { active: !isActive })} />
        <Label htmlFor={hintId} className={cn('ml-2', !isActive && 'opacity-50')} style={{
            overflow: 'hidden',
            display: '-webkit-box',
            WebkitBoxOrient: 'vertical',
            WebkitLineClamp: 2,
          }}>
            {quoteName}
        </Label>
      </div>
      <div className='flex flex-row flex-1 items-center justify-end gap-2'>
        <Button
          variant={viewType === 1 ? 'secondary' : 'ghost'}
          size="icon"
          disabled={!isActive}
          onClick={() => handleClick(quoteId, { type: 1 })}
        >
          <RectangleHorizontal className="w-5 h-5" />
        </Button>
        <Button
          variant={viewType !== 1 ? 'secondary' : 'ghost'}
          size="icon"
          disabled={!isActive}
          onClick={() => handleClick(quoteId, { type: 2 })}
        >
          <Square className="w-5 h-5" />
        </Button>
      </div>
    </div>
  )
}

export { DashboardSubscriptionUpdateMenu }
