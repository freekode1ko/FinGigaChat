import { createBrowserRouter, Navigate } from 'react-router-dom'

import {
  AdminBotPage,
  AdminCommoditiesPage,
  AdminHomePage,
  AdminIndustriesPage,
  AdminSettingsPage,
  AdminUsersPage,
  AdminWhitelistPage,
  AuthPage,
  DashboardPage,
  MeetingsPage,
  NewsPage,
  NotesPage,
  PopularDashboardPage,
  ProfilePage,
  QuoteDetailsPage,
} from '@/pages/ui'
import { WelcomePage } from '@/pages/ui/welcome'
import { ADMIN_MAP, SITE_MAP } from '@/shared/model'

import { adminLayout, baseLayout, emptyLayout } from './layouts'
import { AuthGuard, DevelopGuard } from './router-guard'

export const appRouter = () =>
  createBrowserRouter([
    {
      element: emptyLayout,
      errorElement: <div>error</div>,
      children: [
        {
          path: '/',
          element: <Navigate to="/news" />,
        },
        {
          path: '/quotes',
          element: <Navigate to="/news" />,
        },
        {
          path: SITE_MAP.login,
          element: <AuthPage />,
        },
        {
          path: '/welcome',
          element: <WelcomePage />,
        },
      ],
    },
    {
      element: adminLayout,
      path: ADMIN_MAP.home,
      errorElement: <div>error</div>,
      children: [
        {
          path: '',
          element: (
            <AuthGuard admin>
              <AdminHomePage />
            </AuthGuard>
          ),
        },
        {
          path: ADMIN_MAP.bot,
          element: (
            <AuthGuard admin>
              <AdminBotPage />
            </AuthGuard>
          ),
        },
        {
          path: ADMIN_MAP.settings,
          element: (
            <AuthGuard admin>
              <AdminSettingsPage />
            </AuthGuard>
          ),
        },
        {
          path: ADMIN_MAP.commodities,
          element: (
            <AuthGuard admin>
              <AdminCommoditiesPage />
            </AuthGuard>
          ),
        },
        {
          path: ADMIN_MAP.industries,
          element: (
            <AuthGuard admin>
              <AdminIndustriesPage />
            </AuthGuard>
          ),
        },
        {
          path: ADMIN_MAP.whitelist,
          element: (
            <AuthGuard admin>
              <AdminWhitelistPage />
            </AuthGuard>
          ),
        },
        {
          path: ADMIN_MAP.users,
          element: (
            <AuthGuard admin>
              <AdminUsersPage />
            </AuthGuard>
          ),
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
          element: (
            <AuthGuard>
              <NotesPage />
            </AuthGuard>
          ),
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
