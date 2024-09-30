import { useEffect, useState } from 'react'

import { DashboardSection } from '@/widgets/dashboard-section'
import { ManageDashboardButton } from '@/features/manage-dashboard'
import {
  useGetDashboardSubscriptionsQuery,
  usePutDashboardSubscriptionsMutation,
} from '@/entities/quotes'
import type { DashboardSubscriptionSection } from '@/entities/quotes/model/types'
import { selectUserData } from '@/entities/user'
import { useAppSelector } from '@/shared/lib'

const DashboardPage = () => {
  const user = useAppSelector(selectUserData)
  const { data: initialContent } = useGetDashboardSubscriptionsQuery({ userId: 1 })
  const [trigger] = usePutDashboardSubscriptionsMutation()
  const [pageContent, setPageContent] = useState<
    Array<DashboardSubscriptionSection>
  >([])

  useEffect(() => {
    if (initialContent) {
      setPageContent(initialContent.subscription_sections)
    }
  }, [initialContent])

  const handleSave = async () => {
    if (!user) return
    await trigger({ userId: user.userId, body: pageContent }).unwrap()
    console.log('Dashboard subscriptions updated')
  }

  const handleCancel = () => {
    setPageContent(initialContent ? initialContent.subscription_sections : [])
  }

  return (
    <div className="p-4">
      <ManageDashboardButton
        pageContent={pageContent}
        setPageContent={setPageContent}
        handleSave={handleSave}
        handleCancel={handleCancel}
      />
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
        {pageContent.map((section) => (
          <DashboardSection key={section.section_name} section={section} />
        ))}
      </div>
    </div>
  )
}

export { DashboardPage }
