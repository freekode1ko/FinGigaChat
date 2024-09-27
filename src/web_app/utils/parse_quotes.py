



def parse_moex(json_data: dict[str, Any]) -> list[Quote]:
    quotes = []
    candles = json_data['candles']['data']
    for candle in candles:
        quote = Quote(
            date=candle[0],  # Дата
            open=candle[1],  # Открытие
            high=candle[2],  # Максимум
            low=candle[3],  # Минимум
            close=candle[4],  # Закрытие
            volume=candle[5]  # Объем
        )
        quotes.append(quote)
    return quotes


def parse_cbr(json_data: Dict[str, Any]) -> List[Quote]:
    quotes = []
    rates = json_data.get('ValCurs', {}).get('Record', [])
    for record in rates:
        quote = Quote(
            date=record['@Date'],
            open=float(record['Value'].replace(",", ".")),
            high=0.0,
            low=0.0,
            close=float(record['Value'].replace(",", ".")),
            volume=0
        )
        quotes.append(quote)
    return quotes


def fetch_data(parser: QuoteParser, from_date: str, to_date: str) -> List[Quote]:
    url = parser.url_template.format(from_date=from_date, to_date=to_date, ticker=parser.ticker)
    print(url)
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return parser.parse_function(data)
    else:
        print(f"Ошибка при получении данных для {parser.name}: {response.status_code}")
        return []