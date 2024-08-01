const getWebAppFromGlobal = (): TelegramWebApps.WebApp | null =>
  typeof window !== 'undefined' && window?.Telegram?.WebApp
    ? window.Telegram.WebApp
    : null

const useWebApp = () => {
  return getWebAppFromGlobal()
}

const useInitData = (): readonly [
  TelegramWebApps.WebApp['initDataUnsafe'] | undefined,
  TelegramWebApps.WebApp['initData'] | undefined,
] => {
  const WebApp = useWebApp()
  return [WebApp?.initDataUnsafe, WebApp?.initData]
}

export { useInitData, useWebApp }
