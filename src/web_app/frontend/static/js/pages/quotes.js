const QUOTES_PER_PAGE = 10;
let LOADED_QUOTES = 0;
document.addEventListener("DOMContentLoaded", () => {
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
  const showQuotesLink = document.getElementById("load-quotes");
  showQuotesLink.addEventListener("click", (e) => {
    e.preventDefault();
    renderQuotesData(quotesData);
    if (LOADED_QUOTES >= Object.keys(quotesData).length) {
      showQuotesLink.style.display = "none";
    }
  });
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

function createQuoteCard(key, value) {
  const change = "0.19";
  return `
    <div class="quote-item">
      <p>RUB/${key}</p>
      <div class="quote-value">
          <p>${value}</p>
          <p class="quote-change ${
            parseFloat(change) < 0 ? "negative" : "positive"
          }">${change}%</p>
      </div>
    </div>
  `;
}

function createShortNewsCard(title, text) {
  return `
      <div class="news-item">
          <h2 class="news-title">${title}</h2>
          <p class="news-description truncate-4">${text}</p>
      </div>
    `;
}
