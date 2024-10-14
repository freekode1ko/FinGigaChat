import { Eraser } from 'lucide-react'

import { type Note, useDeleteNoteMutation } from '@/entities/notes'
import { selectUserData } from '@/entities/user'
import { useAppSelector } from '@/shared/lib'
import { Button } from '@/shared/ui'

/*
 * Кнопка для удаления заметки. При нажатии происходит удаление заметки без подтверждения.
 */
const DeleteNoteButton = ({ noteId }: { noteId: Note['id'] }) => {
  const user = useAppSelector(selectUserData)
  const [trigger] = useDeleteNoteMutation()

  if (user) {
    return (
      <Button
        onClick={() => trigger({ userId: user.id, noteId: noteId })}
        variant="ghost"
        size="sm"
        className="w-full justify-start"
      >
        <Eraser /> Удалить
      </Button>
    )
  }
}

export { DeleteNoteButton }
