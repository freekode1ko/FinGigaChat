from __future__ import annotations

from unittest.mock import AsyncMock

import pytest


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
