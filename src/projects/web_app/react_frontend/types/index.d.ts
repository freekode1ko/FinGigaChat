export {}

declare global {
  interface Window {
    Telegram: TelegramWebApps
    onTelegramAuth?: (user: TelegramAuthWidget.CallbackAuthData) => void
    TradingView: unknown
  }
}
