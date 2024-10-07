import { createBrowserRouter } from 'react-router-dom'

import {
  AnalyticDetailsPage,
  AnalyticsPage,
  DashboardPage,
  MeetingsPage,
  NewsPage,
  NotesPage,
  QuoteDetailsPage,
  QuotesPage,
  SubscriptionsPage,
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
          path: '/subscriptions',
          element: (
            <ProtectedWrapper showHomeButton>
              <SubscriptionsPage />
            </ProtectedWrapper>
          ),
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
          path: '/dashboard',
          element: <DashboardPage />,
          children: [
            {
              path: ':quotationId',
              element: <QuoteDetailsPage />,
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
          path: '/notes',
          element: <NotesPage />,
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
