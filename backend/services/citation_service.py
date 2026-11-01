import re
from models.chat import Citation
from models.document import RetrievedChunk

class CitationService:

    def extract_citations(self, answer: str, retrieved_chunks: list[RetrievedChunk]) -> list[Citation]:
        """Find citation markers like [1], [2] in the answer and map
        them to actual source chunks."""

        pattern = r'\[(\d+)\]'
        matches = re.findall(pattern, answer)
        cited_indices = {int(m) for m in matches}

        citations = []
        for idx in sorted(cited_indices):
            chunk_index = idx - 1   # Convert 1-indexed citation → 0-indexed list position
            if 0 <= chunk_index < len(retrieved_chunks):
                chunk = retrieved_chunks[chunk_index]
                citations.append(Citation(
                    citation_number=idx,
                    chunk_id=chunk.chunk_id,
                    doc_id=chunk.doc_id,
                    filename=chunk.filename,
                    page_number=chunk.page_number,
                    text_snippet=chunk.text[:200] + "...",
                    score=chunk.final_score,
                    source_type=chunk.source
                ))
        return citations

    def format_citations_for_display(self, citations: list[Citation]) -> str:
        """Markdown-formatted reference list"""
        if not citations:
            return ""
        lines = ["\n\n**References:**"]
        for c in citations:
            lines.append(
                f"[{c.citation_number}] *{c.filename}*, Page {c.page_number} "
                f"(Relevance: {c.score:.2f})"
            )
        return "\n".join(lines)