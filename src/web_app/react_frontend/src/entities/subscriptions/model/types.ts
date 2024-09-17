export interface SubscriptionUpdate {
  subscription_id: string
  is_subscribed: boolean
}

export interface Subscription {
  name: string
  subscription_id: string
  subscription_type: string
  is_subscribed: boolean
  nearest_menu: Array<Subscription>
}
