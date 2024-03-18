import time
from datetime import datetime
from typing import List

import pandas as pd

from schemas.parser import ParserStatusSend


DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


class ParserStatusFormatter:

    @staticmethod
    def _convert_datetime_to_utc_tz(dt: datetime) -> datetime:
        return datetime.strptime(
            time.strftime(
                DATETIME_FORMAT,
                time.gmtime(
                    time.mktime(
                        time.strptime(
                            dt.strftime(DATETIME_FORMAT),
                            DATETIME_FORMAT,
                        )
                    )
                )
            ),
            DATETIME_FORMAT,
        )

    @classmethod
    def format(cls, data: pd.DataFrame) -> List[ParserStatusSend]:
        res = []
        for i, row in data.iterrows():
            d = row.to_dict()
            if not d['last_update_datetime']:
                del d['last_update_datetime']
            else:
                d['last_update_datetime'] = cls._convert_datetime_to_utc_tz(d['last_update_datetime'])
            if not d['previous_update_datetime']:
                del d['previous_update_datetime']
            else:
                d['previous_update_datetime'] = cls._convert_datetime_to_utc_tz(d['previous_update_datetime'])
            res.append(ParserStatusSend(**d))
        return res

