from models.document import RetrievedChunk

class ContextBuilder:

    def build(self, chunks: list[RetrievedChunk], query: str, max_tokens: int = 4000) -> str:
        """Format retrieved chunks into LLM-ready context. 
        each chunk get a citation marker [1], [2] , etc.."""

        context_parts = []
        current_tokens = 0

        for i, chunk in enumerate(chunk, 1):
            chunk_tokens = len(chunk.text) // 4 # its a rough estimate we are assuming here 1 token = 4 characters

            if current_tokens + chunk_tokens > max_tokens:
                break

            chunk_header = f"[{1}] Source: {chunk.filename} | Page: {chunk.page_number}"
            formatted = f"{chunk_header}\n{chunk.text}"
            context_parts.append(formatted)
            current_tokens += chunk_tokens

        return "\n\n---\n\n".join(context_parts)