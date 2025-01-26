import { CheckIcon, LoaderIcon, PencilIcon, TrashIcon } from "lucide-react"

import { cn } from "@/shared/lib"
import { Badge } from "@/shared/ui"

interface BroadcastBadgeProps {
  deletedAt: Optional<string>,
  createdAt: string,
  isNewest: boolean
}

const BROADCAST_STATUS = {
  SENT: {
    label: 'Отправлено',
    color: 'bg-accent',
    icon: <CheckIcon className="h-4 w-4" />
  },
  IN_PROGRESS: {
    label: 'В процессе',
    color: 'bg-blue-950',
    icon: <LoaderIcon className="h-4 w-4 animate-spin" />
  },
  MODIFIED: {
    label: 'Изменено',
    color: 'bg-secondary',
    icon: <PencilIcon className="h-4 w-4" />
  },
  DELETED: {
    label: 'Удалено',
    color: 'bg-destructive',
    icon: <TrashIcon className="h-4 w-4" />
  },
}

const getBroadcastStatus = ({deletedAt, createdAt, isNewest}: BroadcastBadgeProps) => {
  if (deletedAt) {
    return BROADCAST_STATUS.DELETED
  }

  if (!isNewest) {
    return BROADCAST_STATUS.MODIFIED
  }

  const createDate = new Date(createdAt)
  const fiveMinutesAgo = new Date(Date.now() - 5 * 60 * 1000)
  if (createDate > fiveMinutesAgo) {
    return BROADCAST_STATUS.IN_PROGRESS
  }

  return BROADCAST_STATUS.SENT
}

const BroadcastBadge = (props: BroadcastBadgeProps) => {
  const status = getBroadcastStatus(props)
  return (
    <Badge size='small' className={cn(status.color, 'w-fit gap-2')}>
      {status.icon}
      {status.label}
    </Badge>
  )
}

export { BroadcastBadge }
