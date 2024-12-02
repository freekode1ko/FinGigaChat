// import type { QuotesSection } from '@/entities/quotes/model'
// import { TypographyH2 } from '@/shared/ui'

// import { DashboardItem } from './item'

// interface DashboardSectionProps {
//   section: QuotesSection
// }

// const DashboardSection = ({ section }: DashboardSectionProps) => {
//   if (section.data.length === 0) {
//     return null
//   }
//   return (
//     <div className="w-full space-y-2 mb-8">
//       <div className="py-2 z-50 sticky top-0 bg-background">
//         <TypographyH2>{section.section_name}</TypographyH2>
//       </div>
//       <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
//         {section.data.map((item) => (
//           <DashboardItem key={item.quote_id} item={item} />
//         ))}
//       </div>
//     </div>
//   )
// }

// export { DashboardSection }
