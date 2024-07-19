import React from 'react'
import ReactDOM from 'react-dom/client'
import { Provider as ReduxProvider } from 'react-redux'
import { RouterProvider } from 'react-router-dom'

import { appRouter } from './router.tsx'
import { store } from './store.ts'
import { TelegramWrapper } from './telegram-wrapper.tsx'

import '@/shared/index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <TelegramWrapper>
      <ReduxProvider store={store}>
        <RouterProvider router={appRouter()} />
      </ReduxProvider>
    </TelegramWrapper>
  </React.StrictMode>
)
