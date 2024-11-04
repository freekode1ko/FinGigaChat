import { Outlet } from 'react-router-dom'

import { AnalyticsAccordion, useGetMenusQuery } from '@/entities/analytics'

const AnalyticsPage = () => {
  const { data } = useGetMenusQuery()

  if (data) {
    return (
      <>
        <div className="py-4">
          <h1 className="text-xl font-bold mb-4">{data.title}</h1>
          <AnalyticsAccordion menuItems={data.nearest_menu} />
        </div>
        {/* Analytic Details Drawer */}
        <Outlet />
      </>
    )
  }
}

export { AnalyticsPage }
