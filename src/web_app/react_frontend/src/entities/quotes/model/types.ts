interface QuotesParams {
  readonly name: string
  readonly value: Optional<number>
}

export interface Quotes {
  readonly name: string
  readonly value: Optional<number>
  readonly params: Array<QuotesParams>
  readonly research_item_id: number
  readonly tv_type: string
  readonly image_path: string
}

export interface QuotesSection {
  section_name: string
  section_params: Array<string>
  data: Array<Quotes>
}

export interface TradingViewSymbol {
  name: string
  id: string
}
