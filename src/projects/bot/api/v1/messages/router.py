"""API для работы отправки сообщений"""

from fastapi import APIRouter

from api.v1.messages import schemas
from bot import bot

router = APIRouter(tags=["messages"])


@router.post("/send")
async def send_message(user_msg: schemas.BaseMessage):
    """Отправить сообщение"""
    try:
        await bot.send_message(
            chat_id=user_msg.user_id,
            text=user_msg.message_text,
            parse_mode=user_msg.parse_mode,
        )
    except Exception as e:
        return {'error': str(e)}

    return {"status": "OK"}
