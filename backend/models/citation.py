from pydantic import BaseModel
from typing import Literal, Optional

class Citation(BaseModel):
    citation_number: int
    chunk_id: str
    doc_id: str
    filename: str
    page_number: int
    text_snippet: str
    score: float
    source_type: Literal["vector","graph"]="vector"

    def to_markdown(self) -> str:
        return(
            f"[{self.citation_number}]** `{self.filename}`-"
            f"Page {self.page_number}\n"
            f"> {self.text_snippet[:150]}...\n"
            f"*Relevance: {self.score:.2f} | Retrieved via: {self.source_type}*"
        )
    
class CitationBundle(BaseModel):
    citation=list[Citation]
    total_sources: int
    unique_documents: list[str]

    @classmethod
    def from_citations(cls,citations: list[Citation]) -> "CitationBundle":
        return cls(
            citations=citations,
            total_sources=len(citations),
            unique_documents=list({c.filename for c in citations})
        )