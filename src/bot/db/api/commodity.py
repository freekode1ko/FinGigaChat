from db.api.subject_interface import SubjectInterface
from db.models import Commodity, CommodityAlternative


commodity_db = SubjectInterface(Commodity, CommodityAlternative, Commodity.commodity_alternative)
