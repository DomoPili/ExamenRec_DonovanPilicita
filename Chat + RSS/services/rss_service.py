import feedparser

class RSSService:

    def fetch_and_format(self, url: str) -> str:
        feed = feedparser.parse(url)

        if feed.bozo:
            raise ValueError("URL inválida o RSS no accesible")

        text = f"Fuente: {feed.feed.get('title', 'RSS')}\n\n"

        for entry in feed.entries[:5]:
            text += f"Título: {entry.get('title', '')}\n"
            text += f"Resumen: {entry.get('summary', '')}\n\n"

        return text


