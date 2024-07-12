document.addEventListener("DOMContentLoaded", handleDashboardPageLoading);

async function handleDashboardPageLoading() {
  if (window.location.href.includes("quotes/show")) {
    const dashboardData = await api.quotes.get();
    const newsData = await api.news.get();
    renderDashboard(dashboardData.sections);
    renderNews(newsData.news);
  } else {
    const dashboardData = await api.dashboard.get();
    renderDashboard(dashboardData.sections);
  }
}

function renderDashboard(dashboardData) {
  const dashboardContainer = document.getElementById("dashboard");
  dashboardData.forEach((section) => {
    const sectionBlock = `
      <section class="section">
          <div class="section-header">
              <h2 class="section-title">${section.section_name}</h2>
          </div>
          <div class="quotes-list">
              ${renderCurrencies(section.data)}
          </div>
      </section>
    `;
    dashboardContainer.insertAdjacentHTML("afterbegin", sectionBlock);
  });
}

function renderCurrencies(currencies) {
  return currencies
    .map((currency) => {
      return `
      <div class="quote-item">
          <div>
            <p>${currency.name}</p>
            <h2>${formatPrice(currency.value)}</h2>
          </div>
          <div class="quote-value">
              ${renderCurrencyParameters(currency.params)}
          </div>
      </div>
      `;
    })
    .join("");
}

function renderCurrencyParameters(parameters) {
  return parameters
    .map((parameter) => {
      const { changeClass, changeValue } = parseChange(parameter.value);
      return `
      <span class="quote-details">
          <small>${parameter.name}</small>
          <p class="quote-change ${changeClass}">${changeValue}</p>
      </span>
      `;
    })
    .join("");
}

function renderNews(newsArray) {
  const newsContainer = document.getElementById("news");
  newsArray.forEach((news) => {
    const newsCard = `
      <div class="news-item">
        <h2 class="news-title">${news.title}</h2>
        <p class="news-description truncate-4">${news.text}</p>
      </div>
    `;
    newsContainer.insertAdjacentHTML("beforeend", newsCard);
  });
}
