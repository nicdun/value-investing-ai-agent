from firecrawl import FirecrawlApp, ScrapeOptions

from config.env import FIRECRAWL_API_KEY
from workflow.model import PDFDocument


class FirecrawlAdapter:
    def __init__(self):
        api_key = FIRECRAWL_API_KEY

        if not api_key:
            raise ValueError("FIRECRAWL_API_KEY is not set")

        self.app = FirecrawlApp(api_key=api_key)

        self.ir_patterns = [
            "investor-relations",
            "investors",
            "investor relations",
            "investor",
            "financials",
            "sec-filings",
        ]

        # Quarterly report keywords
        self.quarterly_keywords = [
            "10-Q",
            "10-K",
            "8-K",
            "quarterly report",
            "quarterly earnings",
            "Q1",
            "Q2",
            "Q3",
            "Q4",
            "earnings release",
            "financial results",
            "quarterly results",
        ]

    def search_pages(self, query: str, limit: int = 5) -> list[dict]:
        try:
            result = self.app.search(
                query,
                limit=limit,
                scrape_options=ScrapeOptions(formats=["markdown", "links"]),
            )
            return result.data
        except Exception as e:
            print(f"Error searching Firecrawl: {e}")
            return []

    def scrape_page(self, url: str) -> str:
        try:
            result = self.app.scrape_url(
                url,
                formats=["markdown"],
            )
            return result.data
        except Exception as e:
            print(f"Error scraping Firecrawl: {e}")
            return {}

    def find_investor_relations_pages(
        self, company_name: str, ticker: str
    ) -> list[dict]:
        search_queries = [
            f"{company_name} investor relations",
            f"{ticker} investor relations",
            f"{company_name} quarterly reports",
        ]

        all_results = []
        for query in search_queries:
            results = self.search_pages(query, limit=3)
            all_results.extend(results)

        # Filter for likely IR pages
        ir_pages = []
        for result in all_results:
            url = result.get("url", "").lower()
            title = result.get("title", "").lower()

            # Check if URL or title contains IR patterns
            if any(pattern in url for pattern in self.ir_patterns) or any(
                pattern in title for pattern in self.ir_patterns
            ):
                ir_pages.append(result)

        # Remove duplicates based on URL
        seen_urls = set()
        unique_ir_pages = []
        for page in ir_pages:
            url = page.get("url", "")
            if url not in seen_urls:
                seen_urls.add(url)
                unique_ir_pages.append(page)

        return unique_ir_pages[:2]

    def crawl_quarterly_reports(self, documents: list[PDFDocument]) -> list[dict]:
        reports = []

        for document in documents:
            url = document.url
            if not url or not url.lower().endswith(".pdf"):
                print(f"Skipping non-PDF URL: {url}")
                continue

            try:
                # scrape_page now returns a string (markdown content)
                markdown_content = self.scrape_page(url)

                if not markdown_content:
                    print(f"No content found for {url}")
                    continue

                # Create a report object with the document info and content
                report = {
                    "url": url,
                    "title": document.title,
                    "document_type": document.document_type,
                    "period": document.period,
                    "filename": document.filename,
                    "content": markdown_content,
                    "content_length": len(markdown_content),
                }

                reports.append(report)
                print(
                    f"✅ Successfully crawled {document.title} - {len(markdown_content)} characters"
                )

            except Exception as e:
                print(f"❌ Error crawling {url}: {e}")
                continue

        return reports

    def search_recent_news(self, company_name: str, ticker: str) -> list[dict]:
        """
        Search for recent news about the company
        """
        search_queries = [
            f"{company_name} earnings news",
            f"{ticker} quarterly results",
            f"{company_name} financial news",
            f"{ticker} stock news",
        ]

        all_news = []
        for query in search_queries:
            results = self.search_pages(query, limit=3)
            for result in results:
                # Filter for news-like content
                url = result.get("url", "").lower()
                title = result.get("title", "").lower()

                if any(
                    news_indicator in url
                    for news_indicator in ["news", "press", "article", "blog"]
                ) or any(
                    news_indicator in title
                    for news_indicator in ["news", "report", "analysis", "earnings"]
                ):
                    all_news.append(
                        {
                            "title": result.get("title", "Unknown"),
                            "url": result.get("url", ""),
                            "description": result.get("description", "")[:300] + "..."
                            if len(result.get("description", "")) > 300
                            else result.get("description", ""),
                            "source": result.get("url", ""),
                        }
                    )

        # Remove duplicates
        seen_urls = set()
        unique_news = []
        for news in all_news:
            url = news.get("url", "")
            if url not in seen_urls:
                seen_urls.add(url)
                unique_news.append(news)

        return unique_news[:10]  # Return top 8 news items
