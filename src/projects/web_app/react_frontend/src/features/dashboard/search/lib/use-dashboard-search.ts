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
      .map((section) => {
        const sectionMatches = section.section_name
          .toLowerCase()
          .includes(lowerCaseQuery)
        if (sectionMatches) return section
        const filteredItems = section.subscription_items.filter(
          (item) =>
            item.name.toLowerCase().includes(lowerCaseQuery) ||
            (item.ticker && item.ticker.toLowerCase().includes(lowerCaseQuery))
        )
        return {
          ...section,
          subscription_items: filteredItems,
        }
      })
      .filter((section) => section.subscription_items.length > 0)
  }

  return {
    searchQuery,
    setSearchQuery,
    searchSubscriptions,
  }
}
