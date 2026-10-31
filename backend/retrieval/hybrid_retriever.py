import asyncio
from vector_store.vector_retriever import VectorRetriever
from graph.graph_retriever import GraphRetriever
from retrieval.reranker import SimpleReranker
from retrieval.context_builder import ContextBuilder
from models.document import RetrievedChunk

class HybridRetriever:

    def __init__(self):
        self.vector_retriever = VectorRetriever()
        self.graph_retriever = GraphRetriever()
        self.reranker = SimpleReranker()
        self.context_builder = ContextBuilder()

    async def retrieve(
            self,
            query: str,
            top_k: int = 5,
            doc_ids: list[str] = None,
            vector_weight: float = 0.7,
            graph_weight: float = 0.3
    ) -> tuple[str, list[RetrievedChunk]]:

        # Step 1 : We will be doing Parallel retreival (so if both dbs will be hitted at once it will be faster)

        vector_task = asyncio.to_thread(
            self.vector_retriever.search, query, top_k*2, doc_ids
        )
        graph_task = asyncio.to_thread(
            self.graph_retriever.search, query, top_k*2
        )

        # Step 2 : we will fetch graph-refrenced chunks actual text from qdrant 

        graph_chunks = []
        if graph_chunks_refs:
            chunk_ids = [c["chunk_id"] for c in graph_chunks_refs]
            graph_chunks = self.vector_retriever.fetch_by_ids(chunk_ids)
            for chunk in graph_chunks:
                chunk.score *= graph_weight

        # Apply vector weight

        for chunk in vector_results:
            chunk.score *= vector_weight

        # Step 3 : Merging and Deduplicate

        all_chunks = self._merge_deduplicate(vector_results, graph_chunks)

        # step 4: Re-Rank

        ranked_chunks = self.reranker.rerank(all_chunks, query)

        # step 5 : Take top-k, build context 
        top_chunks = ranked_chunks[:top_k]
        context = self.context_builder.build(top_chunks, query)

        return context, top_chunks

    def _merge_deduplicate(
            self, vector_results: list[RetrievedChunk], graph_results: list[RetrievedChunk]
    ) -> list[RetrievedChunk]:

        chunk_map : dict[str, RetrievedChunk] = {}
        for chunk in vector_results + graph_results:
            if chunk.chunk_id in chunk_map:
                if chunk.score > chunk_map[chunk.chunk_id].score:
                    chunk_map[chunk.chunk_id] = chunk
            else:
                chunk_map[chunk.chunk_id] = chunk

        return list(chunk_map.values())