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
