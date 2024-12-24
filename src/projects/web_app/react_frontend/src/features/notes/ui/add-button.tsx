import { SquarePen } from 'lucide-react'
import { useState } from 'react'

import { selectUserData } from '@/entities/auth'
import { useAppSelector } from '@/shared/lib'
import { Button } from '@/shared/ui'

import { AddNoteForm } from './add-form'

/*
 * Кнопка для добавления заметки. При нажатии в том же месте появляется форма.
 * Возвращается к исходному виду при успешной отправке.
 */
const AddNoteButton = () => {
  const user = useAppSelector(selectUserData)
  const [isFormOpened, setIsFormOpened] = useState<boolean>(false)

  if (user) {
    return (
      <>
        {isFormOpened ? (
          <AddNoteForm afterSubmit={() => setIsFormOpened(false)} />
        ) : (
          <Button onClick={() => setIsFormOpened(true)} variant="ghost">
            <SquarePen /> Добавить заметку
          </Button>
        )}
      </>
    )
  }
}

export { AddNoteButton }
