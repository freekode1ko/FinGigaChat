from pydantic import BaseModel


class MeetingRequest(BaseModel):
    """Тело запроса на создание встречи"""

    user_id: int | str
    theme: str
    date_start: str
    date_end: str
    description: str
    timezone: int
