document.addEventListener("DOMContentLoaded", handleQuotesPageLoading);

async function handleQuotesPageLoading() {
  const quotesData = await api.quotes.get();
  const newsData = await api.news.get();
  const quotesArray = Object.entries(quotesData);
  const quotesState = {
    quotesArray: quotesArray,
    currentPage: 0,
    itemsPerPage: 10,
    totalPages: Math.ceil(quotesArray.length / 10),
  };

  loadQuotes(quotesState);
  document.getElementById("load-quotes").addEventListener("click", (event) => {
    event.preventDefault();
    quotesState.currentPage++;
    loadQuotes(quotesState);
  });
  renderNews(newsData.news);
}

function loadQuotes(state) {
  renderQuotes(state);
  updateLoadMoreButton(state);
}

function updateLoadMoreButton(state) {
  const { currentPage, totalPages } = state;
  const loadMoreButton = document.getElementById("load-quotes");
  loadMoreButton.style.display = currentPage + 1 >= totalPages && "none";
}

function renderQuotes(state) {
  const { quotesArray, currentPage, itemsPerPage } = state;
  const start = currentPage * itemsPerPage;
  const end = start + itemsPerPage;
  const quotesToRender = quotesArray.slice(start, end);
  const quotesContainer = document.getElementById("quotes");

  quotesToRender.forEach(([currencyName, currencyValue]) => {
    const quoteCard = `
      <div class="quote-item">
        <p>RUB/${currencyName}</p>
        <div class="quote-value">
            <p>${formatPrice(currencyValue)}</p>
            <!-- <p class="quote-change></p> -->
        </div>
      </div>
    `;
    quotesContainer.insertAdjacentHTML("beforeend", quoteCard);
  });
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
