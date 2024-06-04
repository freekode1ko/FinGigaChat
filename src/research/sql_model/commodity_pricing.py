"""Модель таблицы commodity_pricing"""
from sqlalchemy import Column, Double, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class CommodityPricing(Base):
    """Класс для взаимодействия с таблицей commodity_pricing"""

    __tablename__ = 'commodity_pricing'

    id = Column(Integer, primary_key=True)
    commodity_id = Column(Integer)
    subname = Column(String)
    unit = Column(String)
    price = Column(Double)
    m_delta = Column(Double)
    y_delta = Column(Double)
    cons = Column(Double)
