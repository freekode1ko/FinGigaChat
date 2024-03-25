import logging

from configs import config
import sentry_sdk
from sentry_sdk.integrations.asyncio import AsyncioIntegration
from sentry_sdk.scrubber import DEFAULT_DENYLIST, EventScrubber

logger = logging.getLogger(__name__)


def init_sentry(dsn: str) -> None:
    """
    Устанавливает интеграцию с Sentry
    dsn: DSN Sentry для интеграции (выдается при создании проекта в Sentry)
    """

    if config.ENV.is_local() and not config.SENTRY_FORCE_LOCAL:
        return

    sentry_sdk.init(
        dsn=dsn,
        environment=config.ENV.value,
        integrations=[AsyncioIntegration()],
        attach_stacktrace=True,
        event_scrubber=EventScrubber(denylist=DEFAULT_DENYLIST),
        include_source_context=True,
        include_local_variables=True,
    )

    logger.info('Sentry initialised')
