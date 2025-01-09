import { Note, SkeletonNoteCard } from '@/entities/notes'
import { PAGE_SIZE } from '@/shared/model'
import { Paragraph } from '@/shared/ui'

import { NoteCardWidget } from './single'

interface NotesListProps {
  notes?: Array<Note>
  showSkeleton?: boolean
}

const NotesList = ({ notes, showSkeleton }: NotesListProps) => {
  return (
    <>
      {notes?.length === 0 && <Paragraph>Нет заметок</Paragraph>}
      <div className="flex flex-col gap-2">
        {showSkeleton &&
          Array.from({ length: PAGE_SIZE }).map((_, idx) => (
            <SkeletonNoteCard key={idx} />
          ))}
        {notes?.map((note) => <NoteCardWidget key={note.id} note={note} />)}
      </div>
    </>
  )
}

export { NotesList }
