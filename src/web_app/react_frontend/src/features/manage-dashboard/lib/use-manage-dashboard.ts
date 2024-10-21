import { useEffect, useState } from 'react'

import {
  useGetDashboardSubscriptionsQuery,
  usePutDashboardSubscriptionsMutation,
} from '@/entities/quotes'
import type {
  DashboardSubscription,
  DashboardSubscriptionSection,
} from '@/entities/quotes/model'
import { selectUserData } from '@/entities/user'
import { useAppSelector } from '@/shared/lib'
import { skipToken } from '@reduxjs/toolkit/query'

export const useManageDashboard = () => {
  const user = useAppSelector(selectUserData)
  const [pageContent, setPageContent] = useState<
    Array<DashboardSubscriptionSection>
  >([])
  const { data: initialContent } = useGetDashboardSubscriptionsQuery(
    user ? { userId: user.id } : skipToken
  )
  const [trigger] = usePutDashboardSubscriptionsMutation()

  const handleSave = async (): Promise<void> => {
    if (!user) return
    await trigger({ userId: user.id, body: pageContent }).unwrap()
  }

  const handleCancel = (): void => {
    setPageContent(initialContent ? initialContent.subscription_sections : [])
  }

  const updatePageContentById = (
    itemId: number,
    updateFn: (item: DashboardSubscription) => DashboardSubscription
  ) => {
    setPageContent((currentContent) => {
      const updatedContent = currentContent.map((section) => ({
        ...section,
        subscription_items: section.subscription_items.map((item) =>
          item.id === itemId ? updateFn(item) : item
        ),
      }))
      return updatedContent
    })
  }

  const handleActiveToggle = (itemId: number): void => {
    updatePageContentById(itemId, (item) => ({
      ...item,
      active: !item.active,
    }))
  }

  const handleTypeChange = (itemId: number, newType: number): void => {
    updatePageContentById(itemId, (item) => ({
      ...item,
      type: newType,
    }))
  }

  const searchSubscriptions = (
    query: string
  ): Array<DashboardSubscriptionSection> => {
    if (!query) return pageContent

    const lowerCaseQuery = query.toLowerCase()

    return pageContent
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

  useEffect(() => {
    if (initialContent) {
      setPageContent(initialContent.subscription_sections)
    }
  }, [initialContent])

  return {
    handleSave,
    handleCancel,
    handleActiveToggle,
    handleTypeChange,
    searchSubscriptions,
  }
}
