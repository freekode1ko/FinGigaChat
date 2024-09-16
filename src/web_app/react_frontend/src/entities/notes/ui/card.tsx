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
  extends Pick<Note, 'client' | 'description' | 'report_date'> {}

export const NoteCard = ({
  client,
  description,
  report_date,
}: NoteCardProps) => {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{client}</CardTitle>
        <CardDescription>{report_date}</CardDescription>
      </CardHeader>
      <CardContent>
        <Paragraph>{description}</Paragraph>
      </CardContent>
    </Card>
  )
}
