import { Link } from 'react-router-dom'

import {
  mapSubscriptionType,
  selectSubscriptionsToUpdate,
  setSubscriptions,
  type Subscription,
  SubscriptionsAccordion,
  updateSubscriptionsToUpdate,
} from '@/entities/subscriptions'
import { useAppDispatch, useAppSelector } from '@/shared/lib'
import { Checkbox, Label } from '@/shared/ui'

interface SubscriptionsAccordionProps {
  subscriptionList: Array<Subscription>
}

const SubscriptionsWidget = ({
  subscriptionList,
}: SubscriptionsAccordionProps) => {
  const dispatch = useAppDispatch()
  const subscriptionsToUpdate = useAppSelector(selectSubscriptionsToUpdate)

  const updateSubscription = (subscriptionId: string, isChecked: boolean) => {
    const updatedList = updateSubscriptionsToUpdate(
      subscriptionsToUpdate,
      subscriptionId,
      isChecked
    )
    dispatch(setSubscriptions(updatedList))
  }

  return (
    <>
      {subscriptionList.map((subscription) =>
        subscription.nearest_menu.length > 0 ? (
          <SubscriptionsAccordion
            subscription={subscription}
            key={subscription.subscription_id}
          >
            <SubscriptionsWidget subscriptionList={subscription.nearest_menu} />
          </SubscriptionsAccordion>
        ) : (
          <div
            className="flex items-center gap-2 [&:not(:last-child)]:mb-4"
            key={subscription.subscription_id}
          >
            <Checkbox
              id={subscription.subscription_id}
              checked={
                subscriptionsToUpdate.find(
                  (update) =>
                    update.subscription_id === subscription.subscription_id
                )?.is_subscribed ?? subscription.is_subscribed
              }
              onCheckedChange={(e) =>
                updateSubscription(subscription.subscription_id, Boolean(e))
              }
            />
            <div className="flex flex-col gap-1">
              <Label htmlFor={subscription.subscription_id}>
                {subscription.name}
              </Label>
              <Link
                to={mapSubscriptionType(subscription.subscription_type).link}
                className="text-sm text-secondary-300 dark:text-secondary-600"
              >
                Перейти к подписке:{' '}
                {mapSubscriptionType(subscription.subscription_type).title}
              </Link>
            </div>
          </div>
        )
      )}
    </>
  )
}

export { SubscriptionsWidget }
