from fastapi import APIRouter, Request

from api.v1.subscriptions.schemas import Subscription

router = APIRouter(tags=['subscriptions'])


@router.get('/menu')
async def get_menu(request: Request) -> Subscription:
    pass


@router.get('/menu/{user_id}')
async def get_menu_with_user_subscriptions(request: Request) -> Subscription:
    pass


@router.get('/{user_id}')
async def get_user_subscriptions(user_id: int) -> Subscription:
    pass


@router.put('/{user_id}/',)
async def update_user_subscriptions(user_id: int) -> Subscription:
    pass
