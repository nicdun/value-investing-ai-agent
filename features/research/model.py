from pydantic import BaseModel


class PDFDocument(BaseModel):
    """
    Represents a PDF document found on investor relations pages.
    """

    url: str
    title: str
    document_type: str  # e.g., "10-K Annual Report", "10-Q Quarterly Report"
    period: str  # e.g., "FY 2024", "FY 2024 Q3"
    filing_date: str | None = None
    filename: str

    def __str__(self) -> str:
        return f"{self.document_type} - {self.period}: {self.title}"


class PDFDocumentList(BaseModel):
    """
    Wrapper for a list of PDF documents for structured output.
    """

    documents: list[PDFDocument]

    def __len__(self) -> int:
        return len(self.documents)

    def __iter__(self):
        return iter(self.documents)

    def __getitem__(self, index):
        return self.documents[index]
