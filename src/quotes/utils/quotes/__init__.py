import utils.quotes.bonds
import utils.quotes.eco
import utils.quotes.exc
import utils.quotes.metals


def get_groups() -> list:
    return [bonds.BondsGetter, eco.EcoGetter, exc.ExcGetter, metals.MetalsGetter]
