import type { SubscriptionUpdate } from '../model'

export const updateSubscriptionsToUpdate = (
  subscriptionsToUpdate: Array<SubscriptionUpdate>,
  subscriptionId: string,
  isSubscribed: boolean
): Array<SubscriptionUpdate> => {
  const existingUpdate = subscriptionsToUpdate.find(
    (update) => update.subscription_id === subscriptionId
  )

  if (existingUpdate) {
    return subscriptionsToUpdate.map((update) =>
      update.subscription_id === subscriptionId
        ? { ...update, is_subscribed: isSubscribed }
        : update
    )
  } else {
    return [
      ...subscriptionsToUpdate,
      { subscription_id: subscriptionId, is_subscribed: isSubscribed },
    ]
  }
}
