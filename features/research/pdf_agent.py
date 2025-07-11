from features.research.model import PDFDocument, PDFDocumentList
from features.llm.google_genai import get_google_genai_llm
from langchain.prompts import PromptTemplate
from ui.cli import get_cli


class PdfAgent:
    def __init__(self):
        self.cli = get_cli()
        self.llm = get_google_genai_llm()

    def extract_pdf_links_with_llm(
        self, ir_pages: list[dict], company_name: str
    ) -> list[PDFDocument]:
        self.cli.show_progress_start("Using LLM to extract PDF links from IR pages...")

        all_pdf_links = []

        for page in ir_pages:
            url = page.get("url", "")
            markdown_content = page.get("markdown", "")

            safe_company_name = "".join(c if c.isalnum() else "_" for c in company_name)
            filename = f"ir_markdown_debug/{safe_company_name}.md"
            try:
                with open(filename, "r", encoding="utf-8") as f:
                    markdown_content_from_file = f.read()
            except Exception as e:
                self.cli.show_progress_error(
                    f"Failed to load markdown content from file: {e}"
                )
                markdown_content_from_file = markdown_content  # fallback

            pdf_links = self._llm_extract_pdfs(
                markdown_content_from_file, company_name, url
            )

            if pdf_links:
                all_pdf_links.extend(pdf_links)
                self.cli.show_progress_success(f"Found {len(pdf_links)} PDF links")
            else:
                self.cli.show_progress_warning("No PDF links found")

        self.cli.show_progress_success(
            f"Total PDF links extracted: {len(all_pdf_links)}"
        )
        return all_pdf_links

    def _llm_extract_pdfs(
        self, markdown_content: str, company_name: str, source_url: str
    ) -> list[PDFDocument]:
        # Create the extraction prompt using the method from prompts.py
        extraction_prompt = PromptTemplate(
            template=self.prompts.extract_pdf_links_from_markdown(),
            input_variables=["company_name", "source_url", "markdown_content"],
        )

        try:
            # Use structured output to get PDFDocumentList directly
            structured_llm = self.llm.with_structured_output(PDFDocumentList)

            formatted_prompt = extraction_prompt.format(
                company_name=company_name,
                source_url=source_url,
                markdown_content=markdown_content[:125000],
            )

            self.cli.show_progress_start("Invoking LLM with structured output...")
            response = structured_llm.invoke(formatted_prompt)

            self.cli.show_progress_success(
                f"Received structured response with {len(response.documents)} documents"
            )

            # Log sample documents
            for document in response.documents:
                self.cli.display_info(
                    f"Sample document: {document.title} - {document.document_type} - {document.url}"
                )

            return response.documents

        except Exception as e:
            self.cli.show_progress_error(f"Error in LLM extraction: {e}")
            return []
