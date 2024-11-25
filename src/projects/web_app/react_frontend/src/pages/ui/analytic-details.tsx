import { useNavigate, useParams } from 'react-router-dom'

import { AnalyticsList } from '@/widgets/analytics-list'
import { CopyPageLinkButton } from '@/features/copy-page-link'
import { useGetSectionQuery } from '@/entities/analytics'
import { useInfiniteScroll } from '@/shared/lib'
import { PAGE_SIZE } from '@/shared/model'
import {
  Drawer,
  DrawerContent,
  DrawerHeader,
  DrawerTitle,
  ShowMoreButton,
} from '@/shared/ui'

const AnalyticDetailsPage = () => {
  const navigate = useNavigate()
  const { analyticId } = useParams() as { analyticId: string }
  const { page, triggerRef } = useInfiniteScroll()
  const { data, isFetching } = useGetSectionQuery({
    page,
    size: PAGE_SIZE,
    sectionId: analyticId,
  })

  return (
    <Drawer open onOpenChange={() => navigate('/analytics')}>
      <DrawerContent className="h-[90vh]">
        <div className="mx-auto w-full pt-6 text-text-color overflow-y-auto">
          <DrawerHeader>
            <DrawerTitle>{data?.title}</DrawerTitle>
          </DrawerHeader>
          <div className="p-2 flex-shrink-0 text-center">
            <CopyPageLinkButton />
          </div>
          <AnalyticsList
            analytics={data?.analytics}
            showSkeleton={isFetching}
            showSendAnalyticsButton
          />
          <ShowMoreButton ref={triggerRef} />
        </div>
      </DrawerContent>
    </Drawer>
  )
}

export { AnalyticDetailsPage }
