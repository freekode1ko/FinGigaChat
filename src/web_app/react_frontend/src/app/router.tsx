import { createBrowserRouter, Navigate } from 'react-router-dom'

import {
  // AnalyticDetailsPage,
  // AnalyticsPage,
  AuthPage,
  DashboardPage,
  MeetingsPage,
  NewsPage,
  NotesPage,
  PopularDashboardPage,
  ProfilePage,
  QuoteDetailsPage,
  // SubscriptionsPage,
} from '@/pages/ui'
import { WelcomePage } from '@/pages/ui/welcome'
import { SITE_MAP } from '@/shared/model'

import { baseLayout, emptyLayout } from './layouts'
import { AuthGuard, DevelopGuard } from './router-guard'

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
          path: SITE_MAP.login,
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
          path: SITE_MAP.news,
          element: <NewsPage />,
        },
        {
          path: SITE_MAP.subscriptions,
          element: <DevelopGuard />,
        },
        {
          path: SITE_MAP.analytics,
          element: <DevelopGuard />,
          children: [
            {
              path: ':analyticId',
              element: <DevelopGuard />,
            },
          ],
        },
        {
          path: SITE_MAP.dashboard + '/popular',
          element: <PopularDashboardPage />,
          children: [
            {
              path: 'quote/:quotationId',
              element: <QuoteDetailsPage />,
            },
          ],
        },
        // FIXME
        {
          path: SITE_MAP.dashboard,
          element: <DashboardPage />,
          children: [
            {
              path: 'quote/:quotationId',
              element: <QuoteDetailsPage />,
            },
          ],
        },
        {
          path: SITE_MAP.dashboard + '/:userId',
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
          path: SITE_MAP.notes,
          element: <AuthGuard><NotesPage /></AuthGuard>,
        },
        {
          path: SITE_MAP.meetings,
          element: (
            <AuthGuard>
              <MeetingsPage />
            </AuthGuard>
          ),
        },
        {
          path: SITE_MAP.profile,
          element: (
            <AuthGuard>
              <ProfilePage />
            </AuthGuard>
          ),
        },
      ],
    },
  ])
