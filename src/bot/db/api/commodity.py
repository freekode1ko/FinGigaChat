"""Запросы к бд связанные с commodity"""
from db.api.subject_interface import SubjectInterface
from db.models import Commodity, CommodityAlternative, RelationCommodityArticle


commodity_db = SubjectInterface(
    Commodity,
    CommodityAlternative,
    Commodity.commodity_alternative,
    RelationCommodityArticle.article,
    RelationCommodityArticle,
)
