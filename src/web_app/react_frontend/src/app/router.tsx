import { createBrowserRouter, Navigate } from 'react-router-dom'

import {
  AnalyticDetailsPage,
  AnalyticsPage,
  AuthPage,
  DashboardPage,
  MeetingsPage,
  NewsPage,
  NotesPage,
  QuoteDetailsPage,
  SubscriptionsPage,
} from '@/pages/ui'
import { WelcomePage } from '@/pages/ui/welcome'

import { baseLayout, emptyLayout } from './layouts/base'
import { ProtectedWrapper } from './router-guard'

export const appRouter = () =>
  createBrowserRouter([
    {
      element: emptyLayout,
      errorElement: <div>error</div>,
      children: [
        {
          path: '/',
          element: <Navigate to='/news' />
        },
        {
          path: '/quotes',
          element: <Navigate to='/news' />
        },
        {
          path: '/login',
          element: <AuthPage />,
        },
        {
          path: '/welcome',
          element: <WelcomePage />
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
        // FIXME
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
        // FIXME
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
