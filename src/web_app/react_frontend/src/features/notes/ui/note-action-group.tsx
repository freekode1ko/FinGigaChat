import { EllipsisVertical } from 'lucide-react'

import type { Note } from '@/entities/notes'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/shared/ui'

import { CopyNoteButton } from './copy-button'
import { DeleteNoteButton } from './delete-button'
import { UpdateNoteButton } from './edit-button'

const NoteActionGroup = ({
  note,
  onEdit,
}: {
  note: Note
  onEdit: () => void
}) => {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger>
        <EllipsisVertical />
      </DropdownMenuTrigger>
      <DropdownMenuContent>
        <DropdownMenuItem>
          <CopyNoteButton noteText={note.description} />
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem>
          <UpdateNoteButton note={note} onEdit={onEdit} />
        </DropdownMenuItem>
        <DropdownMenuItem>
          <DeleteNoteButton noteId={note.id} />
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}

export { NoteActionGroup }
