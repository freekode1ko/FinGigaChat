import type {
  DashboardSubscriptionSection,
  FlattenedDashboardItem,
} from '../model'

/*
Превращает список секций с котировками в плоский список, который содержит как секции,
так и котировки. Возвращает плоский список объектов FlattenedDashboardItem.
*/
export const flattenQuotesContent = (
  content: Array<DashboardSubscriptionSection>
): Array<FlattenedDashboardItem> => {
  const flattened: Array<FlattenedDashboardItem> = []
  content.forEach((section) => {
    flattened.push({
      type: 'section',
      sectionName: section.section_name,
    })
    section.subscription_items.forEach((item) => {
      flattened.push({
        type: 'item',
        item,
      })
    })
  })
  return flattened
}
