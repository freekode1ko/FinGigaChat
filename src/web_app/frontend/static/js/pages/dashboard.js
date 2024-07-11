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
              value: 0.01,
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
              value: null,
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
          exchange_rate: 145200,
          parameters: [
            {
              name: "Δ day",
              value: 1.2,
            },
            {
              name: "YTD",
              value: -5.44,
            },
          ],
        },
      ],
    },
  ],
};

document.addEventListener("DOMContentLoaded", () =>
  renderDashboard(FAKE_DATA.sections)
);

function renderDashboard(dashboardData) {
  const dashboardContainer = document.getElementById("dashboard");
  dashboardData.forEach((section) => {
    const sectionBlock = `
      <section class="section">
          <div class="section-header">
              <h2 class="section-title">${section.section_title}</h2>
          </div>
          <div class="quotes-list">
              ${renderCurrencies(section.currencies)}
          </div>
      </section>
    `;
    dashboardContainer.insertAdjacentHTML("beforeend", sectionBlock);
  });
}

function renderCurrencies(currencies) {
  return currencies
    .map((currency) => {
      return `
      <div class="quote-item">
          <p>${currency.currency_name}</p>
          <div class="quote-value">
              <p>${formatPrice(currency.exchange_rate)}</p>
              ${renderCurrencyParameters(currency.parameters)}
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
