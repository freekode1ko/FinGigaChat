const API_URL = "https://ai-bankir-helper-dev.ru/";
const tgObj = window.Telegram.WebApp;

document.addEventListener("DOMContentLoaded", () => {
  applyTgTheme(tgObj.themeParams);
  lucide.createIcons();
});

function applyTgTheme(themeParams) {
  const root = document.documentElement;
  Object.keys(themeParams).forEach((param) => {
    const cssVarName = `--${param.replace(/_/g, "-")}`;
    root.style.setProperty(cssVarName, themeParams[param]);
  });
}
