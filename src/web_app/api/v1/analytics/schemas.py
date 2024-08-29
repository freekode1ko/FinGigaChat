from typing import Optional

from pydantic import BaseModel


class AnalyticsElement(BaseModel):
    """Схема для отображения элементов в разделе аналитика"""

    analytic_id: int
    section: str
    title: str
    text: str
    date: str


class AnalyticsMenu(BaseModel):
    """Схема для отображения меню в разделе аналитика"""

    title: str
    analytics_menu_id: Optional[int] = None
    nearest_menu: list['AnalyticsMenu'] = []
