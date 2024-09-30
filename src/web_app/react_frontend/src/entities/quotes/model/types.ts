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

export interface DashboardSubscription {
  id: number
  name: string
  active: boolean
  type: number
}

export interface DashboardSubscriptionSection {
  section_name: string
  subscription_items: Array<DashboardSubscription>
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

export interface FinancialData {
  date: Date
  value: number
  open: number | null
  close: number | null
  high: number | null
  low: number | null
  volume: number | null
}
