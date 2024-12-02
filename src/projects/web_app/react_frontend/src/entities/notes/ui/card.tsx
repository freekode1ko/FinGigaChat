import type { Note } from '@/entities/notes'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  Paragraph,
} from '@/shared/ui'

interface NoteCardProps
  extends Pick<Note, 'client' | 'description' | 'report_date'> {
  actionSlot?: React.ReactNode
}

export const NoteCard = ({
  client,
  description,
  report_date,
  actionSlot,
}: NoteCardProps) => {
  return (
    <Card>
      <CardHeader>
        <div className="flex justify-between">
          <CardTitle>{client}</CardTitle>
          {actionSlot}
        </div>
        <CardDescription>{report_date}</CardDescription>
      </CardHeader>
      <CardContent>
        <Paragraph>{description}</Paragraph>
      </CardContent>
    </Card>
  )
}
