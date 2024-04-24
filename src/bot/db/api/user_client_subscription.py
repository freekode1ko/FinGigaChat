from db.api.subscriptions_interface import SubscriptionInterface
from db.models import UserClientSubscriptions, Client


user_client_subscription_db = SubscriptionInterface(UserClientSubscriptions, 'client_id', Client)
