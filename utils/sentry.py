import logging

import sentry_sdk
from sentry_sdk.integrations.asyncio import AsyncioIntegration
import config
from sentry_sdk.scrubber import DEFAULT_DENYLIST, EventScrubber
from enums import Environment

logger = logging.getLogger(__name__)


def init_sentry(dsn: str) -> None:
    """
    Устанавливает интеграция с Sentry
    dsn: DSN Sentry для интеграции (выдается при создании проекта в Sentry)
    """

    if config.ENV == Environment.LOCAL and not config.SENTRY_FORCE_LOCAL:
        return

    sentry_sdk.init(
        dsn=dsn,
        environment=config.ENV.value,
        integrations=[AsyncioIntegration()],
        event_scrubber=EventScrubber(
            denylist=DEFAULT_DENYLIST
        ),
        include_source_context=True,
        include_local_variables=True,
    )

    logger.info('Sentry initialised')
