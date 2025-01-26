import { ChevronDown, Dot } from "lucide-react"
import { useState } from "react"

import { cn } from "@/shared/lib"
import { Button, Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/shared/ui"

import type { FullBroadcast } from "../model"
import { BroadcastBadge } from "./broadcast-badge"

interface BroadcastCardProps {
  broadcast: FullBroadcast
  isNewest: boolean
  actionSlot?: React.ReactNode
}

const BroadcastCard = ({broadcast, isNewest, actionSlot}: BroadcastCardProps) => {
  const [isExpanded, setIsExpanded] = useState(false)

  return (
    <Card className="relative">
      <div className="absolute top-0 right-0">{actionSlot}</div>
      <CardHeader>
        <CardTitle dangerouslySetInnerHTML={{__html: broadcast.message_text.length > 40 ? broadcast.message_text.slice(0, 40) + '...' : broadcast.message_text}} />
        <BroadcastBadge
          deletedAt={broadcast.deleted_at}
          createdAt={broadcast.create_at}
          isNewest={isNewest}
        />
      </CardHeader>
      <CardContent dangerouslySetInnerHTML={{__html: isExpanded ? broadcast.message_text : (broadcast.message_text.length > 200 ? broadcast.message_text.slice(0, 200) + '...' : broadcast.message_text)}} className="space-y-2" />
      <CardFooter>
        <CardDescription>{new Date(broadcast.create_at).toLocaleDateString()}</CardDescription>
        <Dot className="h-4 w-4 text-muted-foreground" />
        <CardDescription>{broadcast.author_id}</CardDescription>
      </CardFooter>
      {broadcast.message_text.length > 200 && (
        <Button className="pt-1 w-full" variant='ghost' onClick={() => setIsExpanded(!isExpanded)}>
          <span>{isExpanded ? 'Свернуть' : 'Развернуть'}</span>
          <ChevronDown className={cn("h-4 w-4 transition-transform", isExpanded && 'rotate-180')} />
        </Button>
      )}
    </Card>
  )
}

export {BroadcastCard}
