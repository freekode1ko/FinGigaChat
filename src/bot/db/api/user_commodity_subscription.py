from db.api.subscriptions_interface import SubscriptionInterface
from db.models import UserCommoditySubscriptions, Commodity


user_commodity_subscription_db = SubscriptionInterface(UserCommoditySubscriptions, 'commodity_id', Commodity)
