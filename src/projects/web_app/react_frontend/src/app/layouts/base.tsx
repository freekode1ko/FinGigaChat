import { Header } from '@/widgets/header'
import { NavigationTabs } from '@/widgets/navigation'
import { AdminButton } from '@/features/admin-button'
import { Layout } from '@/shared/ui'

export const baseLayout = (
  <Layout headerSlot={<Header />} bottomMenuSlot={<NavigationTabs />} adminButtonSlot={<AdminButton />} />
)
