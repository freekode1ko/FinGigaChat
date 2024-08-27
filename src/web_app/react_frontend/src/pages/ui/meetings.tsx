import { MeetingsList } from '@/widgets/meetings-list'
import { AddMeetingButton } from '@/features/add-meeting'
import { useGetMeetingsQuery } from '@/entities/meetings'
import { selectUserData } from '@/entities/user'
import { useAppSelector } from '@/shared/lib'
import { TypographyH2 } from '@/shared/ui'

// можно убрать "!"
const MeetingsPage = () => {
  const user = useAppSelector(selectUserData)
  const { data, isFetching } = useGetMeetingsQuery({userId: user!.userId})

  return (
    <>
      <div className="flex justify-between py-2">
        <TypographyH2>Встречи</TypographyH2>
        <AddMeetingButton userId={user!.userId} />
      </div>
      <MeetingsList
        meetings={data}
        showSkeleton={isFetching}
      />
    </>
  )
}

export { MeetingsPage }
