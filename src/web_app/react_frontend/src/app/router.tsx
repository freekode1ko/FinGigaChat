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
            <ProtectedWrapper>
              <SubscriptionsPage />
            </ProtectedWrapper>
          ),
        },
        {
          path: '/analytics',
          element: (
            <ProtectedWrapper>
              <AnalyticsPage />
            </ProtectedWrapper>
          ),
          children: [
            {
              path: ':analyticId',
              element: (
                <ProtectedWrapper>
                  <AnalyticDetailsPage />
                </ProtectedWrapper>
              ),
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
          element: <ProtectedWrapper><NotesPage /></ProtectedWrapper>,
        },
        {
          path: '/meetings',
          element: (
            <ProtectedWrapper>
              <MeetingsPage />
            </ProtectedWrapper>
          ),
        },
      ],
    },
  ])
