interface CommodityResearch {
  id: number
  title?: string
  text: string
  url: Optional<string>
}

interface CreateCommodityResearch {
  title?: string
  text: string
  file: Optional<File>
}

interface ShortCommodity {
  id: number
  name: string
  industry_id?: number
}

interface Commodity extends ShortCommodity {
  commodity_research: Array<CommodityResearch>
}

export type {
  Commodity,
  CommodityResearch,
  CreateCommodityResearch,
  ShortCommodity,
}
