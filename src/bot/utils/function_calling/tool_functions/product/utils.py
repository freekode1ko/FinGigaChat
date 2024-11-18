"""Вспомогательные функции для тулзы по продуктам"""
from db import models


def get_root_id(product: models.Product, products: list[models.Product]) -> int:
    """Поиск корневого продукта

    :param product:  Продукт
    :param products: Список всех продуктов

    :return: ID корневого продукта
    """
    while True:
        if product.parent_id is None:
            raise Exception
        if product.parent_id == 0:
            return product.id
        product = next(filter(lambda x: x.id == product.parent_id, products))
