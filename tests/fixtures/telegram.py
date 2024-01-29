from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
from aiogram.exceptions import TelegramBadRequest
from aiogram.methods.send_message import SendMessage


@pytest.fixture
def tg_chat_id() -> int:
    return 451795185


@pytest.fixture
def tg_from_user_full_name() -> str:
    return 'Test user'


@pytest.fixture
def tg_message_text() -> str:
    return 'Test telegram message text'


@pytest.fixture
def tg_message_too_long_text() -> str:
    return 'Bad Request: text is too long'


@pytest.fixture
def tg_message_too_long_error(tg_message_too_long_text, tg_chat_id, tg_message_text) -> Exception:
    return TelegramBadRequest(message=tg_message_too_long_text, method=SendMessage(chat_id=tg_chat_id, text=tg_message_text))


@pytest.fixture
def tg_unhandled_error_msg() -> str:
    return 'Unhandled test error'


@pytest.fixture
def tg_unhandled_error(tg_unhandled_error_msg, tg_chat_id, tg_message_text) -> Exception:
    return TelegramBadRequest(message=tg_unhandled_error_msg, method=SendMessage(chat_id=tg_chat_id, text=tg_message_text))


@pytest.fixture
def bot_handler_message_too_long_error(tg_message_too_long_error) -> AsyncMock:
    return AsyncMock(side_effect=tg_message_too_long_error)


@pytest.fixture
def tg_message(tg_chat_id, tg_from_user_full_name, tg_message_text) -> AsyncMock:
    """
    Мок для сообщения aiogram
    При необходимости можно добавлять поля, созданием новой fixture
    """
    msg_mock = AsyncMock()
    msg_mock.chat.id = tg_chat_id
    msg_mock.from_user.full_name = tg_from_user_full_name
    msg_mock.text = tg_message_text
    return msg_mock
