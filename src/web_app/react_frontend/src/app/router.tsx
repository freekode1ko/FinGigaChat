import { createBrowserRouter } from 'react-router-dom'

import {
  AnalyticDetailsPage,
  AnalyticsPage,
  AuthPage,
  DashboardPage,
  MeetingsPage,
  NewsPage,
  NotesPage,
  QuoteDetailsPage,
  QuotesPage,
  SubscriptionsPage,
} from '@/pages/ui'

import { baseLayout, emptyLayout } from './layouts/base'
import { ProtectedWrapper } from './router-guard'

export const appRouter = () =>
  createBrowserRouter([
    {
      element: emptyLayout,
      errorElement: <div>error</div>,
      children: [
        {
          path: '/login',
          element: <AuthPage />,
        },
      ],
    },
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
        //
        {
          path: '/dashboard',
          element: <DashboardPage />,
          children: [
            {
              path: 'quote/:quotationId',
              element: <QuoteDetailsPage />,
            },
          ],
        },
        {
          path: '/dashboard/:userId',
          element: <DashboardPage />,
          children: [
            {
              path: 'quote/:quotationId',
              element: <QuoteDetailsPage />,
            },
          ],
        },
        //
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
