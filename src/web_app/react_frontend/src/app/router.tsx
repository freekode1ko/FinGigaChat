import { createBrowserRouter } from 'react-router-dom'

import {
  AnalyticDetailsPage,
  AnalyticsPage,
  DashboardPage,
  MeetingsPage,
  NewsPage,
  QuoteDetailsPage,
  QuotesPage,
} from '@/pages/ui'

import { baseLayout } from './layouts/base'
import { ProtectedWrapper } from './router-guard'

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
          path: '/analytics',
          element: <AnalyticsPage />,
          children: [
            {
              path: ':analyticId',
              element: <AnalyticDetailsPage />,
            },
          ],
        },
        {
          path: '/quotes',
          element: <QuotesPage />,
          children: [
            {
              path: ':quotationId',
              element: <QuoteDetailsPage />,
            },
          ],
        },
        {
          path: '/',
          element: <DashboardPage />,
        },
        {
          path: '/meetings',
          element: (
            <ProtectedWrapper showHomeButton>
              <MeetingsPage />
            </ProtectedWrapper>
          ),
        },
      ],
    },
  ])
