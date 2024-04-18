from db.api.subscriptions_interface import SubscriptionInterface
from db.models import UserIndustrySubscriptions, Industry


user_industry_subscription_db = SubscriptionInterface(UserIndustrySubscriptions, 'industry_id', Industry)
