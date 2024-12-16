interface IndustryDocument {
  id: number
  name: string
  url: string
}

interface CreateIndustryDocument {
  name: string
  file: File
}

interface Industry {
  id: number
  name: string
  display_order: number
  documents: Array<IndustryDocument>
}

interface CreateIndustry {
  name: string
  display_order: number
}

export type {
  CreateIndustry,
  CreateIndustryDocument,
  Industry,
  IndustryDocument,
}
