import {
  Card,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/shared/ui'

import type { Meeting } from '../model'

interface MeetingCardProps extends Meeting {}

export const MeetingCard = ({theme, date_start}: MeetingCardProps) => {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{theme}</CardTitle>
        <CardDescription>{date_start}</CardDescription>
      </CardHeader>
    </Card>
  )
}
