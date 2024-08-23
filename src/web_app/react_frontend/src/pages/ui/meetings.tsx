import { AddMeetingButton } from '@/features/add-meeting'
import { useGetMeetingsQuery } from '@/entities/meetings'
import { useInitData } from '@/shared/lib'
import { Paragraph, TypographyH2 } from '@/shared/ui'

const MeetingsPage = () => {
  const [userData] = useInitData()
  const { data, isLoading } = useGetMeetingsQuery({
    userId: userData?.user?.id || 1,
  })

  return (
    <>
      <div className="flex justify-between py-2">
        <TypographyH2>Встречи</TypographyH2>
        <AddMeetingButton />
      </div>
      <div>
        {(!data || isLoading) && <div>Загрузка...</div>}
        {data?.length === 0 && <div>Нет будущих встреч</div>}
        {data?.map((meeting, meetingIdx) => (
          <div key={meetingIdx}>
            <Paragraph>{meeting.theme}</Paragraph>
            <Paragraph>{meeting.date_start}</Paragraph>
          </div>
        ))}
      </div>
    </>
  )
}

export { MeetingsPage }
