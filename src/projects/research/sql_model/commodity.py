"""Модель таблицы commodity"""
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Commodity(Base):
    """Класс для взаимодействия с таблицей commodity"""

    __tablename__ = 'commodity'

    id = Column(Integer, primary_key=True)
    name = Column(String)
