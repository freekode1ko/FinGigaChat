import { ChevronDown } from "lucide-react"
import { useState } from "react"

import { UserRole } from "@/entities/user"
import { cn } from "@/shared/lib"
import { Button, Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/shared/ui"

const BroadcastCard = ({broadcast, actionSlot}: {broadcast: {id: number, title: string, content: string, created_at: Date, roles: Array<UserRole>}, actionSlot?: React.ReactNode}) => {
  const [isExpanded, setIsExpanded] = useState(false)

  return (
    <Card className="relative">
      {actionSlot && <div className="absolute top-0 right-0">{actionSlot}</div>}
      <CardHeader>
        <CardTitle>{broadcast.content.length > 40 ? broadcast.content.slice(0, 40) + '...' : broadcast.content}</CardTitle>
        <CardDescription>{broadcast.created_at.toLocaleDateString()}</CardDescription>
      </CardHeader>
      <CardContent>
        <p>{isExpanded ? broadcast.content : (broadcast.content.length > 200 ? broadcast.content.slice(0, 200) + '...' : broadcast.content)}</p>
      </CardContent>
      <CardFooter>
        <p className="text-sm text-muted-foreground">Получатели: {broadcast.roles.map(role => role.name).join(', ')}</p>
      </CardFooter>
      {broadcast.content.length > 200 && (
        <Button className="pt-1 w-full" variant='ghost' onClick={() => setIsExpanded(!isExpanded)}>
          <span>{isExpanded ? 'Свернуть' : 'Развернуть'}</span>
          <ChevronDown className={cn("h-4 w-4 transition-transform", isExpanded && 'rotate-180')} />
        </Button>
      )}
    </Card>
  )
}

export {BroadcastCard}
