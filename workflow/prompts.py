class Prompts:
    STOCK_ANALYSIS_BASE = """You are a financial analysis agent. Your task is to analyze the fundamental data of a given stock using a variety of specialized tools. Carefully review the company's financial statements, key ratios, and any relevant market data provided by the tools at your disposal. 
    Your goal is to determine whether the stock represents a good investment opportunity."""

    @staticmethod
    def analyze_ticker_user(
        company_name: str, ticker: str, reports_summary: str, news_summary: str
    ) -> str:
        return f"""
            Analyze the following research findings for {company_name} ({ticker}):

            QUARTERLY REPORTS FOUND:
            {reports_summary}

            RECENT NEWS:
            {news_summary}

            Please provide a comprehensive analysis that includes:
            1. Summary of key findings from quarterly reports
            2. Analysis of recent news sentiment and impact
            3. Identification of any red flags or positive indicators
            4. provide an overview for the companies risks
            5. Assessment of recent financial performance trends
            6. Market sentiment and analyst opinions (if available) 

            Format your response as a structured analysis report.
            """

    @staticmethod
    def extract_pdf_links_from_markdown() -> str:
        return """
You are a financial document analyst. Analyze the following markdown content from an investor relations page and extract information about PDF documents related to quarterly reports, annual reports, and SEC filings.

Company: {company_name}
Source URL: {source_url}

Markdown Content:
{markdown_content}

INSTRUCTIONS:
1. Look for PDF download links (URLs ending in .pdf)
2. Focus on these document types:
   - Quarterly Reports (10-Q, Q1, Q2, Q3, Q4, quarterly earnings)
   - Annual Reports (10-K, annual report, annual earnings)
   - SEC Filings (8-K, proxy statements, registration statements)
   - Earnings releases and financial results

3. For each PDF found, extract:
   - Direct PDF URL (url field)
   - Document title/name (title field)
   - Document type: classify as one of: "10-K Annual Report", "10-Q Quarterly Report", "8-K Current Report", "Quarterly Financial Statements", "Annual Financial Statements", "Earnings Release", "Proxy Statement", "Registration Statement", "Additional Financial Report", "Green Bond Report", "Capital Return History Report"
   - Filing period/quarter: Format as "FY 2024", "FY 2024 Q3", "Q1 2024", "2024", etc. (period field)
   - Filing date if mentioned (filing_date field, can be null)
   - Filename: extract from URL (filename field)

IMPORTANT: 
- Only include actual PDF download links, not general page links
- Focus on the most recent documents: last 2 Annual reports (10-K) and last 4 quarterly reports (10-Q)
- Order the reports from newest to oldest in the output list
- Ensure all URLs are complete and downloadable
- Classify document types accurately based on content and filename
- Extract periods in consistent format (FY YYYY, FY YYYY QX, etc.)

Return a list of documents with all required fields populated.
        """
