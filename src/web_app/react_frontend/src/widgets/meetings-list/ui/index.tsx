import { type Meeting, MeetingCard, SkeletonMeetingCard } from '@/entities/meetings'
import { PAGE_SIZE } from '@/shared/model'
import { Paragraph } from '@/shared/ui'

interface MeetingsListProps {
  meetings?: Array<Meeting>
  showSkeleton?: boolean
}

const MeetingsList = ({
  meetings,
  showSkeleton
}: MeetingsListProps) => {
  return (
    <>
      {meetings?.length === 0 && <Paragraph>Нет встреч</Paragraph>}
      <div className="flex flex-col gap-2">
        {showSkeleton &&
          Array.from({ length: PAGE_SIZE }).map((_, idx) => (
            <SkeletonMeetingCard key={idx} />
          ))
        }
        {meetings?.map((meeting, meetingIdx) => (
          <MeetingCard
            theme={meeting.theme}
            date_start={meeting.date_start}
            key={meetingIdx}
          />
        ))}
      </div>
    </>
  )
}

export { MeetingsList }
