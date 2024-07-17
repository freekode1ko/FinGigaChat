document.addEventListener("DOMContentLoaded", () => {
  const tgObj = window.Telegram.WebApp;
  applyTgTheme(tgObj.themeParams);
  lucide.createIcons();
});

function applyTgTheme(themeParams) {
  const root = document.documentElement;
  Object.keys(themeParams).forEach((param) => {
    const cssVarName = `--${param.replace(/_/g, "-")}`;
    root.style.setProperty(cssVarName, themeParams[param]);
  });
  document.body.style.visibility = "visible";
}
