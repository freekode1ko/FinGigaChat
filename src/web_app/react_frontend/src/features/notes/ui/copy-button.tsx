import { Clipboard } from 'lucide-react'

import { type Note } from '@/entities/notes'
import { Button } from '@/shared/ui'

/*
 * Кнопка копирования текста заметки. При нажатии происходит копирование текста в буфер обмена.
 */
const CopyNoteButton = ({ noteText }: { noteText: Note['description'] }) => {
  return (
    <Button
      onClick={() => navigator.clipboard.writeText(noteText)}
      variant="ghost"
      size="sm"
      className="w-full justify-start"
    >
      <Clipboard /> Скопировать текст
    </Button>
  )
}

export { CopyNoteButton }
