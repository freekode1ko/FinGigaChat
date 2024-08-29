import { createBrowserRouter } from 'react-router-dom'

import {
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
          path: '/quotes',
          element: <QuotesPage />,
          children: [
            {
              path: '/quotes/:quotationId',
              element: <QuoteDetailsPage />,
            },
          ],
        },
        {
          path: '/',
          element: <DashboardPage />,
        },
        // {
        //   path: '/analytics',
        //   element: <AnalyticsPage />,
        // },
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
