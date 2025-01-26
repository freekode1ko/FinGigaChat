import { Dot } from "lucide-react"

import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/shared/ui"

import type { Broadcast } from "../model"
import { BroadcastBadge } from "./broadcast-badge"

interface BroadcastCardProps {
  broadcast: Broadcast
  isNewest: boolean
}

const BroadcastVersionCard = ({broadcast, isNewest}: BroadcastCardProps) => {
  return (
    <Card>
      <CardHeader>
        <CardTitle dangerouslySetInnerHTML={{__html: broadcast.message_text.length > 40 ? broadcast.message_text.slice(0, 40) + '...' : broadcast.message_text}} />
        <BroadcastBadge
          deletedAt={null}
          createdAt={broadcast.create_at}
          isNewest={isNewest}
        />
      </CardHeader>
      <CardContent dangerouslySetInnerHTML={{__html: broadcast.message_text}} className="space-y-2" />
      <CardFooter>
        <CardDescription>{new Date(broadcast.create_at).toLocaleDateString()}</CardDescription>
        <Dot className="h-4 w-4 text-muted-foreground" />
        <CardDescription>{broadcast.author_id}</CardDescription>
      </CardFooter>
    </Card>
  )
}

export { BroadcastVersionCard }
