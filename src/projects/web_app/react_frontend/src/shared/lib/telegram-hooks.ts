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

const useThemeParams = (): readonly [
  TelegramWebApps.WebApp['themeParams'] | undefined,
  TelegramWebApps.WebApp['colorScheme'] | undefined,
] => {
  const WebApp = useWebApp()
  return [WebApp?.themeParams, WebApp?.colorScheme]
}

export { getWebAppFromGlobal, useInitData, useThemeParams, useWebApp }
