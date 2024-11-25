from fastapi import APIRouter, Request, status
from faker import Faker

from api.v1.subscriptions.schemas import Subscription, DetailSubscriptionsResponse, SubscriptionTypeEnum

router = APIRouter(tags=['subscriptions'])


# @router.get('/menu')
# async def get_menu(request: Request) -> Subscription:
#     pass


@router.get('/{user_id}')
async def get_menu_with_user_subscriptions(user_id: int, request: Request) -> Subscription:
    fake = Faker()
    def generate_subscriptions(depth) -> Subscription:
        if depth <= 1:
            return Subscription(
                name=fake.sentence(nb_words=6),
                subscription_id=fake.unique.random_int(min=1, max=999999),
                subscription_type=SubscriptionTypeEnum.analytics_reports,
                is_subscribed=fake.random_int(min=0, max=1)
            )
        return Subscription(
            name=fake.sentence(nb_words=6),
            subscription_id=fake.unique.random_int(min=1, max=999999),
            subscription_type=SubscriptionTypeEnum.analytics_reports,
            nearest_menu=[generate_subscriptions(depth - fake.random_int(min=1, max=depth)) for _ in range(fake.random_int(min=3, max=5))]
        )
    return generate_subscriptions(5)


@router.get('/{user_id}/{subscription_id}')
async def get_user_subscriptions(user_id: int, subscription_id: int) -> DetailSubscriptionsResponse:
    fake = Faker()
    return DetailSubscriptionsResponse(
        subscription_id=subscription_id,
        name=fake.sentence(nb_words=10),
        subscriptions=[
            Subscription(
                subscription_id=fake.unique.random_int(min=1, max=999999),
                name=fake.sentence(nb_words=10),
                subscription_type=SubscriptionTypeEnum.analytics_reports,
            ) for _ in range(10)
        ]
    )


@router.put('/{user_id}', status_code=status.HTTP_202_ACCEPTED)
async def update_user_subscriptions(user_id: int) -> None:
    return None
