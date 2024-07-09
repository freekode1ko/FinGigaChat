const FAKE_DATA = {
  sections: [
    {
      section_title: "Популярные валюты",
      currencies: [
        {
          currency_name: "RUB/USD",
          exchange_rate: 120,
          parameters: [
            {
              name: "Δ day",
              value: -0.5,
            },
            {
              name: "YTD",
              value: 12.3,
            },
          ],
        },
        {
          currency_name: "RUB/JPY",
          exchange_rate: 60,
          parameters: [
            {
              name: "Δ day",
              value: -0.5,
            },
            {
              name: "YTD",
              value: 12.3,
            },
          ],
        },
      ],
    },
    {
      section_title: "Драгоценные металлы, $/унц",
      currencies: [
        {
          currency_name: "Золото",
          exchange_rate: 2372,
          parameters: [
            {
              name: "Δ day",
              value: 1.2,
            },
            {
              name: "YTD",
              value: 5.44,
            },
          ],
        },
      ],
    },
  ],
};

document.addEventListener("DOMContentLoaded", () =>
  renderDashboardData(FAKE_DATA)
);

function renderDashboardData(dashboardData) {
  const dashboardElement = document.getElementById("dashboard");
  dashboardElement.innerHTML = dashboardData.sections
    .map(createDashboardSection)
    .join("");
}

function createDashboardSection(section) {
  return `
        <section class="section">
            <div class="section-header">
                <h2 class="section-title">${section.section_title}</h2>
            </div>
            <div class="quotes-list">
                ${section.currencies.map(createCurrency).join("")}
            </div>
        </section>
    `;
}

function createCurrency(currency) {
  return `
    <div class="quote-item">
        <p>${currency.currency_name}</p>
        <div class="quote-value">
            <p>${currency.exchange_rate}</p>
            ${currency.parameters.map(createCurrencyParameters).join("")}
      </div>
    </div>
    `;
}

function createCurrencyParameters(parameter) {
  return `
    <span class="quote-details">
        <small>${parameter.name}</small>
        <p class="quote-change ${
          parseFloat(parameter.value) < 0 ? "negative" : "positive"
        }">${parameter.value}%</p>
    </span>
    `;
}
