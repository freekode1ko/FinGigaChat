import { SubscriptionsWidget } from '@/widgets/subscribition-accordion'
import { ManageSubscriptionsButtonGroup } from '@/features/manage-subscriptions'
import { useGetSubscriptionsQuery } from '@/entities/subscriptions'
import { selectUserData } from '@/entities/auth'
import { useAppSelector } from '@/shared/lib'
import { skipToken } from '@reduxjs/toolkit/query'

const SubscriptionsPage = () => {
  const user = useAppSelector(selectUserData)
  const { data: initialData } = useGetSubscriptionsQuery(
    user
      ? {
          userId: user.id,
        }
      : skipToken
  )

  if (initialData) {
    return (
      <>
        <div className="pt-10 pb-4">
          <h1 className="text-xl font-bold mb-4">Меню подписок</h1>
          <SubscriptionsWidget subscriptionList={[initialData]} />
        </div>
        <ManageSubscriptionsButtonGroup />
      </>
    )
  }
}

export { SubscriptionsPage }
