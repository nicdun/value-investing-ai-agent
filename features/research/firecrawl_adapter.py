from firecrawl import FirecrawlApp, ScrapeOptions
from config.env import FIRECRAWL_API_KEY

class FirecrawlAdapter:
    def __init__(self):
        api_key=FIRECRAWL_API_KEY

        if not api_key:
            raise ValueError("FIRECRAWL_API_KEY is not set")
        
        self.app = FirecrawlApp(api_key=api_key)

    def search_company_pages(self, query: str, limit: int = 5) -> list[dict]:
        try:
            result = self.app.search(query, limit=limit, scrape_options=ScrapeOptions(
            formats=["markdown"]
            ))
            return result
        except Exception as e:
            print(f"Error searching Firecrawl: {e}")
            return []
        
    
    def scrape_company_pages(self, url: str) -> dict:
        try:
            result = self.app.scrape_url(url, scrape_options=ScrapeOptions(
                include_content=True,
                include_pdfs=True,
                formats=["markdown"]
            ))
            return result
        except Exception as e:
            print(f"Error scraping Firecrawl: {e}")
            return {}