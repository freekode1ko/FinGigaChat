export interface QuotesParams {
  readonly name: string
  readonly value: number
}

export interface Quotes {
  name: string
  ticker: Optional<string>
  value: number
  params: Array<QuotesParams>
  view_type: number
  quote_id: number
  image_path: string

  // legacy
  tv_type: string
  research_item_id: string
}

export interface DashboardSubscription {
  id: number
  name: string
  ticker: Optional<string>
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
  open: Optional<number>
  close: Optional<number>
  high: Optional<number>
  low: Optional<number>
  volume: Optional<number>
}

export interface FlattenedDashboardItem {
  type: 'section' | 'item'
  sectionName?: string
  item?: DashboardSubscription
}
