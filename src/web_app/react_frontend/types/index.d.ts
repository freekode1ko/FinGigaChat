export {}

declare global {
  interface Window {
    Telegram: TelegramWebApps
    onTelegramAuth?: (user: TelegramWebApps.WebAppUser) => void
    TradingView: unknown
  }
}
