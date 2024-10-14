import { NavigationTabs } from '@/widgets/navigation'
import { Layout } from '@/shared/ui'

export const baseLayout = <Layout bottomMenuSlot={<NavigationTabs />} />

export const emptyLayout = <Layout />
