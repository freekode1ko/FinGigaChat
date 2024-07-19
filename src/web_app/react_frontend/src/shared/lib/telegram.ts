export const applyTelegramTheme = (theme: TelegramWebApps.ThemeParams) => {
  const root = document.documentElement
  for (const [key, value] of Object.entries(theme)) {
    if (value) {
      root.style.setProperty(`--${key}`, value)
    }
  }
}
