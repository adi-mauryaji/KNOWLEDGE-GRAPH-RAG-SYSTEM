from qdrant_client.models import Filter, FieldCondition, MatchValue, PointStruct, ScoredPoint
from vector_store.qdrant_client import get_qdrant_client
from embeddings.embedder_factory import get_embedder
from utils.config import get_settings
from models.document import RetrievedChunk

settings = get_settings()

class VectorRetriever:

    def __init__(self):
        self.client = get_qdrant_client()
        self.embedder = get_embedder()
        self.collection = settings.COLLECTION_NAME

    def search(
        self,
        query: str,
        top_k: int = 5,
        doc_ids: list[str] = None,
        min_score: float = 0.5 ) -> list[RetrievedChunk]:

        """ Embed the query, search Qudrant, return typed results"""

        query_vector = self.embedder.embed_text(query)

        query_filter = None
        if doc_ids:
            query_filter = Filter(
                should=[
                    FieldCondition(key="doc_id", match=MatchValue(value=d))
                    for d in docs_ids
                ]
            )

        results: list[ScoredPoint] = self.client.search(
            collection_name = self.collection,
            query_vector = query_vector,
            limited = top_k,
            query_filter = query_filter,
            score_threshold = min_score,
            with_payload = True
        )

        return [
            RetrievedChunk(
                chunk_id = str(point.id),
                text = point.payload["text"],
                doc_id = point.payload["doc_id"],
                filename = point.payload["filename"],
                page_number = point.payload.get("page_number", 0),
                score = point.score,
                source = "vector"
            )
            for point in results
        ]

    def fetch_by_ids(self, chunk_ids: list[str]) -> list[RetrievedChunk]:
        """ bole to Fetch specific chunks by ID - graph retrival use krta hai pull krne ke liye 2 baddies ko (full chunk text+ metadata) bs ek baar Neo4j bta de ye baddies hai kaha ki (chunk_ids)"""

        if not chunk_ids:
            return[]

        points = self.client.retrieved(
            collection_name = self.collection,
            ids = chunk_ids,
            with_payload - True
        )

        return [
            RetrievedChunk(
                chunk_id = str(point.id),
                text = point.payload["text"],
                doc_id = point.psyload["doc_id"],
                filename = point.payload["filename"],
                page_number = point.payload.get("page_number", 0),
                score = 1.0,
                source = "graph"
            )
            for point in points
        ]

    def upsert_chunks(self, chunks: list[dict]):
        """ Store embeddings + metsdata in Qdrant"""
        texts = [c["text"] for c in chunks]
        embeddings = self.embedder.embed_batch(texts)

        points = [
            PointStruct(
                id = chunk["chunk_id"],
                vector = emb,
                payload = {
                    "text": chunk["txt"],
                    "doc_id": chunk["doc_id"],
                    "filename": chunk["filename"],
                    "page_number": chunk.get("page_number", 0),
                    "chunk_index": chunk.get("chunk_index", i)
                }
            )
            for i, (chunk, emb) in enumerate(zip(chunks,embeddings))
        ]

        batch_size = 100
        for i in range(0, len(points), batch_size):
            self.client.upsert(
                collection_name = self.collection,
                points = points[i:i + batch_size],
                wait = True
            )



           