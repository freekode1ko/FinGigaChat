interface QuotesParams {
  name: string
  value: Optional<number>
}

export interface Quotes {
  name: string
  value: Optional<number>
  params: Array<QuotesParams>
}
