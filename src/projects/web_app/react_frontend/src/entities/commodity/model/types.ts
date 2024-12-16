interface CommodityResearch {
  id: number
  title?: string
  text: string
  url: string
}

interface CreateCommodityResearch {
  title?: string
  text: string
  file: File
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
