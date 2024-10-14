import { useState } from 'react'

import type { DashboardSubscriptionSection } from '@/entities/quotes'

export const useDashboardSearch = (
  content: Array<DashboardSubscriptionSection>
) => {
  const [searchQuery, setSearchQuery] = useState<string>('')

  const searchSubscriptions = (
    query: string
  ): Array<DashboardSubscriptionSection> => {
    if (!query) return content

    const lowerCaseQuery = query.toLowerCase()

    return content
      .map((section) => ({
        ...section,
        subscription_items: section.subscription_items.filter(
          (item) =>
            item.name.toLowerCase().includes(lowerCaseQuery) ||
            (item.ticker && item.ticker.toLowerCase().includes(lowerCaseQuery))
        ),
      }))
      .filter((section) => section.subscription_items.length > 0)
  }

  return {
    searchQuery,
    setSearchQuery,
    searchSubscriptions,
  }
}
