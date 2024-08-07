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

export type PopularQuotes =
  | 'TVC:GOLD'
  | 'TVC:SILVER'
  | 'TVC:PLATINUM'
  | 'BLACKBULL:BRENT'
  | 'FX_IDC:CNYRUB'
  | 'FX_IDC:USDCNY'
