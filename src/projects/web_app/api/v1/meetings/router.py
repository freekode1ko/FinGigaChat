from fastapi import APIRouter
from fastapi.responses import JSONResponse

import config
import utils
from db.meeting import add_meeting, get_user_email, get_user_meetings
from log.logger_base import selector_logger

from .schemas import MeetingRequest

logger = selector_logger(config.LOG_FILE, config.LOG_LEVEL)
router = APIRouter(tags=['meetings'])


@router.post('/', status_code=201)
async def create_meeting(meeting: MeetingRequest) -> str:
    data = meeting.model_dump()
    data = utils.reformat_data(data)
    meeting_id = await add_meeting(data)
    logger.info('Встреча %s пользователя %s сохранена в бд', meeting.theme, meeting.user_id)
    data['meeting_id'] = meeting_id
    await utils.add_notify_job(logger=logger, meeting=data)
    user_email = await get_user_email(user_id=meeting.user_id)
    with (utils.SmtpSend(config.MAIL_RU_LOGIN, config.MAIL_RU_PASSWORD, config.MAIL_SMTP_SERVER, config.MAIL_SMTP_PORT)
          as smtp_email):
        smtp_email.send_meeting(user_email, data)
    logger.info('Информация о встрече %s пользователя %s отправлена на почту', meeting.theme, meeting.user_id)
    return 'OK'


@router.get("/{user_id}", response_class=JSONResponse)
async def show_user_meetings(user_id: int | str):
    meetings = await get_user_meetings(user_id)
    meetings = utils.format_date(meetings)
    logger.info('Пользователю %s показано %d встреч', user_id, len(meetings))
    return JSONResponse(meetings)
