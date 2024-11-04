import { RefreshCcw } from 'lucide-react'

import { type Note } from '@/entities/notes'
import { selectUserData } from '@/entities/user'
import { useAppSelector } from '@/shared/lib'
import { Button } from '@/shared/ui'

/*
 * Кнопка для удаления заметки. При нажатии происходит удаление заметки без подтверждения.
 */
const UpdateNoteButton = ({
  note,
  onEdit,
}: {
  note: Note
  onEdit: () => void
}) => {
  const user = useAppSelector(selectUserData)

  if (user) {
    return (
      <Button
        onClick={onEdit}
        variant="ghost"
        size="sm"
        className="w-full justify-start"
      >
        <RefreshCcw /> Редактировать
        <span className="sr-only">{note.id}</span>
      </Button>
    )
  }
}

export { UpdateNoteButton }
