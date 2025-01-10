export const API_ENDPOINTS = {
  popularQuotes: 'quotation/popular',
  dashboardQuotes: 'quotation/dashboard',
  news: 'news',
  meetings: 'meetings',
  analytics: 'analytics',
  subscriptions: 'subscriptions',
  notes: 'notes',
  auth: 'auth',
  products: 'products',
  settings: 'settings',
  commodities: 'commodities',
  industries: 'industries',
  users: 'users',
  bot: 'bot',
}

export const API_TAGS = {
  meetings: 'MEETINGS',
  notes: 'NOTES',
  dashboard: 'DASHBOARD',
  dashboardSubscriptions: 'DASHBOARD_SUBSCRIPTIONS',
  dashboardQuotes: 'DASHBOARD_QUOTES',
  settings: 'SETTINGS',
  products: 'PRODUCTS',
  commodities: 'COMMODITIES',
  industries: 'INDUSTRIES',
  users: 'USERS',
}

export const SITE_MAP = {
  quotes: '/quotes',
  dashboard: '/dashboard',
  news: '/news',
  meetings: '/meetings',
  analytics: '/analytics',
  subscriptions: '/subscriptions',
  notes: '/notes',
  profile: '/profile',
  login: '/login',
}

export const ADMIN_MAP = {
  home: '/admin',
  settings: '/admin/settings',
  commodities: '/admin/commodities',
  whitelist: '/admin/whitelist',
  industries: '/admin/industries',
  users: '/admin/users',
  bot: '/admin/bot',
}

export const DESKTOP_MEDIA_QUERY = '(min-width: 768px)'
export const PAGE_SIZE = 10
export const KEEP_UNUSED_DATA_TEMP = 120
export const KEEP_UNUSED_DATA_INF = Infinity
export const DEV_API_URL = 'http://localhost:8000/api/v1'
export const GRAPH_POLLING_INTERVAL = 15 * 60 * 1000
