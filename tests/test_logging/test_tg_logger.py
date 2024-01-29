import logging

import pytest

from tests.utils.assertion import assert_words_in_text


@pytest.mark.parametrize(
    'level',
    (
        logging.INFO,
        logging.DEBUG,
        logging.WARNING,
        logging.CRITICAL,
        logging.ERROR,
    ),
)
def test_log_tg_meta(level, tg_message, tg_logger, caplog, tg_chat_id, tg_message_text, tg_from_user_full_name):
    caplog.set_level(level)

    handler = tg_logger.get_callable_by_level(level)
    handler(tg_msg=tg_message, msg='Text')
    assert_words_in_text(words=[str(tg_chat_id), tg_message_text, tg_from_user_full_name], text=caplog.text)
