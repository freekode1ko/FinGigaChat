import { createBrowserRouter } from 'react-router-dom'

import { DashboardPage, NewsPage, QuotesPage } from '@/pages/ui'

import { baseLayout } from './layouts/base'

export const appRouter = () =>
  createBrowserRouter([
    {
      element: baseLayout,
      errorElement: <div>error</div>,
      children: [
        {
          path: '/news',
          element: <NewsPage />,
        },
        {
          path: '/quotes',
          element: <QuotesPage />,
        },
        {
          path: '/',
          element: <DashboardPage />,
        },
      ],
    },
  ])
