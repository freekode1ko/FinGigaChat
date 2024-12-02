import { AdminHeader } from '@/widgets/header'
import { NavigationList, NavigationSheet } from '@/widgets/navigation'
import { Layout } from '@/shared/ui'

export const adminLayout = (
  <Layout
    sidebarSlot={
      <div className="sticky top-0 p-4">
        <NavigationList dir="vertical" content="admin" />
      </div>
    }
    headerSlot={<AdminHeader navigationSlot={<NavigationSheet />} />}
  />
)
