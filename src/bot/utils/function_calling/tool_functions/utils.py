"""Вспомогательный функции и классы для работы function calling"""

import dataclasses
from typing import Any

from aiogram import types
from langchain_core.runnables import RunnableConfig


@dataclasses.dataclass
class LanggraphConfig:
    message: types.Message

    def config_to_langgraph_format(self) -> dict[str, dict[str, Any]]:
        """Превращает конфиг из класса в словарь для langgraph"""
        return {'configurable': self.__dict__}


def parse_runnable_config(config: RunnableConfig) -> LanggraphConfig:
    return LanggraphConfig(
        **{
            k: v
            for k, v in config['configurable'].items()
            if k in LanggraphConfig.__dataclass_fields__ and isinstance(v, LanggraphConfig.__dataclass_fields__[k].type)
        }
    )
