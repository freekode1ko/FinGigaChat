import logging
from unittest.mock import AsyncMock

import pytest
from aiogram.exceptions import TelegramBadRequest

from utils.error_handlers import handle_telegram_bad_request_error


async def test_handle_bad_request_error__too_long(bot_handler_message_too_long_error, caplog, tg_message_text):
    caplog.set_level(logging.ERROR)

    try:
        await bot_handler_message_too_long_error()
    except TelegramBadRequest as err:
        handle_telegram_bad_request_error(err)

    assert tg_message_text in caplog.text
    assert 'MessageIsTooLong' in caplog.text
    bot_handler_message_too_long_error.assert_awaited_once()


async def test_handle_message_too_long_error__unhandled(caplog, tg_unhandled_error_msg, tg_unhandled_error):
    caplog.set_level(logging.ERROR)
    route = AsyncMock(side_effect=tg_unhandled_error)

    with pytest.raises(TelegramBadRequest) as err:
        try:
            await route()
        except TelegramBadRequest as err:
            handle_telegram_bad_request_error(err)

        assert err.message == tg_unhandled_error_msg

    assert tg_unhandled_error_msg in caplog.text
    route.assert_awaited_once()
