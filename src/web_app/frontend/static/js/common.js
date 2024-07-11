class Endpoint {
  constructor(baseURL, endpoint) {
    this.baseURL = baseURL;
    this.endpoint = endpoint;
  }

  async get(params = {}) {
    let url = new URL(`${this.baseURL}/${this.endpoint}`);
    Object.keys(params).forEach((key) =>
      url.searchParams.append(key, params[key])
    );
    try {
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`Ошибка API. Статус: ${response.status}`);
      }
      const data = await response.json();
      return data;
    } catch (error) {
      console.error("Неизвестная ошибка:", error);
      throw error;
    }
  }
}

class WebAppAPI {
  constructor(baseURL) {
    this.baseURL = baseURL;
    this.news = new Endpoint(this.baseURL, "news/");
    this.quotes = new Endpoint(this.baseURL, "quotation/RUB");
  }
}

const api = new WebAppAPI("https://ai-bankir-helper-dev.ru");

function parseChange(value) {
  const parsedValue = parseFloat(value);
  return {
    changeClass:
      parsedValue < 0 ? "negative" : parsedValue >= 0 ? "positive" : "neutral",
    changeValue: value ? value.toString().concat("%") : "—",
  };
}

function formatPrice(value) {
  if (typeof value === "string") {
    value = parseInt(value, 10);
  }
  return value.toLocaleString("ru-RU");
}
