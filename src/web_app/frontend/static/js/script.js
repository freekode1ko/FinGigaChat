const API_URL = "https://127.0.0.1:443/";
const QUOTES_PER_PAGE = 10;
let LOADED_QUOTES = 0;

document.addEventListener("DOMContentLoaded", () => {
  lucide.createIcons();
  const CURRENT_URL = window.location.href;
  if (CURRENT_URL.includes("/quotation/")) {
    let quotesData;
    fetch(API_URL.concat("quotation/RUB"))
      .then((response) => response.json())
      .then((data) => {
        quotesData = data;
        renderQuotesData(quotesData);
      })
      .catch((err) => console.error("Котировки не были загружены", err));

    fetch(API_URL.concat("news/"))
      .then((response) => response.json())
      .then((data) => renderShortNewsData(data.news))
      .catch((err) => console.error("Новости не были загружены", err));

    const showQuotesButton = document.getElementById("load-quotes");
    showQuotesButton.addEventListener("click", () => {
      renderQuotesData(quotesData);
      if (LOADED_QUOTES >= Object.keys(quotesData).length) {
        showQuotesButton.style.display = "none";
      }
    });
  } else if (CURRENT_URL.includes("/news/")) {
    fetch(API_URL.concat("news/"))
      .then((response) => response.json())
      .then((data) => renderNewsData(data.news))
      .catch((err) => console.error("Новости не были загружены", err));
  }
});

function renderQuotesData(quotesData) {
  const quotesElement = document.getElementById("quotes");
  const quotesKeys = Object.keys(quotesData);
  const quotesToRender = quotesKeys.slice(
    LOADED_QUOTES,
    LOADED_QUOTES + QUOTES_PER_PAGE
  );
  quotesToRender.forEach((quoteKey) => {
    const quoteCardHTML = createQuoteCard(quoteKey, quotesData[quoteKey]);
    quotesElement.innerHTML += quoteCardHTML;
  });
  LOADED_QUOTES += quotesToRender.length;
}

function renderShortNewsData(newsData) {
  const newsElement = document.getElementById("news");
  newsData.forEach((news) => {
    const newsCardHTML = createShortNewsCard(news.title, news.text);
    newsElement.innerHTML += newsCardHTML;
  });
}

function renderNewsData(newsData) {
  const newsElement = document.getElementById("news");
  newsData.forEach((news) => {
    const newsCardHTML = createNewsCard(
      news.title,
      news.text,
      news.section,
      news.date
    );
    newsElement.innerHTML += newsCardHTML;
  });
}

function createShortNewsCard(title, text) {
  return `
    <div class="news-item">
        <h2 class="news-title">${title}</h2>
        <p class="news-description truncate-4">${text}</p>
    </div>
  `;
}

function createNewsCard(title, text, section, date) {
  return `
    <div class="news-item">
        <p class="news-info">${section}</p>
        <h2 class="news-title">${title}</h2>
        <p class="news-description">${text}</p>
    </div>
  `;
}

function createQuoteCard(key, value) {
  return `
    <div class="quote-item">
      <p>RUB/${key}</p>
      <div class="quote-value">
          <p>${value}</p>
          <!-- <p class="quote-change negative">-0.19%</p> -->
      </div>
    </div>
  `;
}
