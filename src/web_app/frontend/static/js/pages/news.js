document.addEventListener("DOMContentLoaded", () => {
  lucide.createIcons();
  fetch(API_URL.concat("news/"))
    .then((response) => response.json())
    .then((data) => renderNewsData(data.news))
    .catch((err) => console.error("Новости не были загружены", err));
});

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

function createNewsCard(title, text, section, date) {
  return `
    <div class="news-item">
        <p class="news-info">${section}</p>
        <h2 class="news-title">${title}</h2>
        <p class="news-description">${text}</p>
    </div>
  `;
}
