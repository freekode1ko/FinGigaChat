import type { FinancialData } from '@/entities/quotes'

export const mapFinancialData = (data: Array<FinancialData>) =>
  data.map((d) => ({
    date: new Date(d.date),
    value: d.value,
    open: d.open,
    high: d.high,
    low: d.low,
    close: d.close,
    volume: d.volume,
  }))
