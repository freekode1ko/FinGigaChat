import { NotesList } from '@/widgets/notes-list'
import { AddNoteButton } from '@/features/notes'
import { type Note, useGetNotesQuery } from '@/entities/notes'
import { selectUserData } from '@/entities/user'
import { useAppSelector } from '@/shared/lib'
import { skipToken } from '@reduxjs/toolkit/query'

const NotesPage = () => {
  const user = useAppSelector(selectUserData)
  const { isFetching } = useGetNotesQuery(
    user ? { userId: user.id } : skipToken
  )

  const data = [
    {
      id: '1',
      client: 'Позвонить туда',
      description: 'Не забыть позвонить...',
      report_date: '13.09.2024',
    },
    {
      id: '2',
      client: 'Сходить сюда',
      description: 'Завтра сходить...',
      report_date: '12.09.2024',
    },
  ] as Array<Note>

  return (
    <div className="mx-auto lg:max-w-screen-sm pt-5 pb-2 space-y-2">
      <AddNoteButton />
      <NotesList notes={data} showSkeleton={isFetching} />
    </div>
  )
}

export { NotesPage }
