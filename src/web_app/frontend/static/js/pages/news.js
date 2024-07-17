document.addEventListener("DOMContentLoaded", handleNewsPageLoading);

async function handleNewsPageLoading() {
  const newsState = {
    currentPage: 1,
    itemsPerPage: 10,
    totalPages: null,
  };

  loadNews(newsState);
  document
    .getElementById("load-news")
    .addEventListener("click", async (event) => {
      event.preventDefault();
      newsState.currentPage++;
      await loadNews(newsState);
    });
}

async function loadNews(state) {
  const newsData = await api.news.get({
    page: state.currentPage,
    size: state.itemsPerPage,
  });
  state.totalPages = newsData.total;
  renderNews(newsData.news);
  updateLoadMoreButton(state);
}

function updateLoadMoreButton(state) {
  const { currentPage, totalPages } = state;
  const loadMoreButton = document.getElementById("load-news");
  loadMoreButton.style.display = currentPage + 1 >= totalPages && "none";
}

function renderNews(newsData) {
  const newsContainer = document.getElementById("news");
  newsData.forEach((news) => {
    const newsCard = `
      <div class="news-item">
          <p class="news-info">${news.section}</p>
          <h2 class="news-title">${news.title}</h2>
          <p class="news-description">${news.text}</p>
      </div>
    `;
    newsContainer.insertAdjacentHTML("beforeend", newsCard);
  });
}
