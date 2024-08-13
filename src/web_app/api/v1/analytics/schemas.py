from typing import Optional

from pydantic import BaseModel


class AnalyticsElement(BaseModel):
    """"""  # FIXME

    analytic_id: int
    section: str
    title: str
    text: str
    date: str


class AnalyticsMenu(BaseModel):
    """"""  # FIXME

    name: str
    analytics_menu_id: Optional[int] = None
    nearest_menu: list['AnalyticsMenu'] = []
