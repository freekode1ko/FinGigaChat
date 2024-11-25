import { MeetingsList } from '@/widgets/meetings-list'
import { AddMeetingButton } from '@/features/add-meeting'
import { useGetMeetingsQuery } from '@/entities/meetings'
import { selectUserData } from '@/entities/user'
import { useAppSelector } from '@/shared/lib'
import { TypographyH2 } from '@/shared/ui'

const MeetingsPage = () => {
  const user = useAppSelector(selectUserData)
  const { data, isFetching } = useGetMeetingsQuery({ userId: user!.id })

  return (
    <div className='mx-auto lg:max-w-screen-sm pt-5 pb-2 space-y-2'>
      <div className="py-2 px-4 border-b border-border flex justify-between items-center gap-4 h-16">
        <TypographyH2>Встречи</TypographyH2>
        <AddMeetingButton />
      </div>
      <MeetingsList meetings={data} showSkeleton={isFetching} />
    </div>
  )
}

export { MeetingsPage }
