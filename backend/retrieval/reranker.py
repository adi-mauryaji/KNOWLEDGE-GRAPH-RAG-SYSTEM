from models.document import RetrievedChunk

class SimpleReranker:

    """ This will rerank based on 
    1. Base similarity/weighted score
    2. Boost for graph-discovered chunks (structural relevance signal)
    3. Keyword overlap boost (lexical signal, complements semantic similarity)

    """

    def rerank(self, chunks: list[RetrievedChunk], query : str) -> list[RetrievedChunk]:
        for chunk in chunks:
            final_score = chunk.score

            if chunk.source == "graph":
                final_score *= 1.1

            query_words = set(query.lower().split())
            chunk_words = set(chunk.text.lower().split())
            overlap = len(query_words & chunk_words) / max(len(query_words), 1)
            final_score += overlap * 0.1

            chunk.final_score = min(final_score, 0.1)

        return sorted(chunks, key=lambda x: x.final_score, reverse=True)