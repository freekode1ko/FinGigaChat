import { useState } from 'react'

import { NoteActionGroup, UpdateNoteForm } from '@/features/notes'
import { type Note, NoteCard } from '@/entities/notes'

const NoteCardWidget = ({ note }: { note: Note }) => {
  const [isEdit, setIsEdit] = useState<boolean>(false)
  return (
    <>
      {isEdit ? (
        <UpdateNoteForm note={note} onEdited={() => setIsEdit(false)} />
      ) : (
        <NoteCard
          key={note.id}
          client={note.client}
          description={note.description}
          report_date={note.report_date}
          actionSlot={
            <NoteActionGroup note={note} onEdit={() => setIsEdit(true)} />
          }
        />
      )}
    </>
  )
}

export { NoteCardWidget }
