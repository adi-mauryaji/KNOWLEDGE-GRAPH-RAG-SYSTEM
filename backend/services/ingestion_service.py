import asyncio
import datetime
import time
from pathlib import Path
from fastapi import UploadFile

from ingestion.pdf_loader import PDFLoader
from ingestion.text_cleaner import TextCleaner
from ingestion.chunker import Chunker, ChunkingStrategy
from vector_store.vector_retriever import VectorRetriever
from graph.entity_extractor import EntityExtractor
from graph.graph_builder import GraphBuilder
from models.document import DocumentMetadata, Chunk
from models.chat import DocumentUploadResponse
from utils.config import get_settings
from utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()

# Simple in-memory document store (replace with PostgreSQL for production scale)
_document_store: dict[str, DocumentMetadata] = {}


class IngestionService:
    """Orchestrates the full PDF → Qdrant + Neo4j ingestion pipeline"""

    def __init__(self):
        self.loader = PDFLoader()
        self.cleaner = TextCleaner()
        self.chunker = Chunker(
            strategy=ChunkingStrategy(settings.CHUNKING_STRATEGY),
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
        )
        self.vector_retriever = VectorRetriever()
        self.entity_extractor = EntityExtractor()
        self.graph_builder = GraphBuilder()

    async def process_document(self, file: UploadFile, doc_id: str) -> DocumentUploadResponse:
        """Full pipeline: Upload → save → parse → clean → chunk → embed+store → extract → graph"""
        start = time.time()

        # 1. Save uploaded file
        upload_dir = Path(settings.UPLOAD_DIR)
        upload_dir.mkdir(parents=True, exist_ok=True)
        file_path = upload_dir / f"{doc_id}_{file.filename}"

        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        logger.info(f"[{doc_id}] Saved file: {file.filename} ({len(content)} bytes)")

        meta = DocumentMetadata(
            doc_id=doc_id, filename=file.filename, file_hash="",
            file_size_bytes=len(content), total_pages=0, status="processing",
        )
        _document_store[doc_id] = meta

        try:
            # 2. Load PDF
            documents = self.loader.load(str(file_path), doc_id)
            meta.total_pages = len(documents)
            meta.file_hash = self.loader._compute_hash(str(file_path))

            # 3. Clean
            for doc in documents:
                doc.text = self.cleaner.clean(doc.text)

            # 4. Chunk
            nodes = self.chunker.chunk(documents)
            chunks = [
                Chunk(
                    doc_id=doc_id, text=node.text,
                    page_number=int(node.metadata.get("page_label", 0) or 0),
                    chunk_index=node.metadata.get("chunk_index", i),
                    chunk_total=len(nodes), filename=file.filename,
                )
                for i, node in enumerate(nodes)
            ]
            meta.total_chunks = len(chunks)

            # 5. Embed + Store in Qdrant
            chunk_dicts = [c.model_dump() for c in chunks]
            self.vector_retriever.upsert_chunks(chunk_dicts)
            logger.info(f"[{doc_id}] Stored {len(chunks)} chunks in Qdrant")

            # 6. Entity extraction + Graph
            if not settings.SKIP_EXTRACTION:
                total_entities, total_rels = await self._extract_and_build_graph(chunks, doc_id)
                meta.entities_extracted = total_entities
                meta.relationships_extracted = total_rels

            # 7. Mark complete
            meta.status = "completed"
            meta.processed_at = datetime.datetime.now()
            elapsed_ms = int((time.time() - start) * 1000)
            logger.info(f"[{doc_id}] Ingestion complete in {elapsed_ms}ms")

            return DocumentUploadResponse(
                doc_id=doc_id, filename=file.filename, status="completed",
                chunks_created=meta.total_chunks, entities_extracted=meta.entities_extracted,
                message=f"Processed {meta.total_pages} pages into {meta.total_chunks} chunks",
            )

        except Exception as e:
            meta.status = "failed"
            meta.error_message = str(e)
            logger.error(f"[{doc_id}] Ingestion failed: {e}", exc_info=True)
            raise

    async def _extract_and_build_graph(self, chunks: list[Chunk], doc_id: str) -> tuple[int, int]:
        """Extract entities from all chunks concurrently (max 5 at a time), write to Neo4j"""
        semaphore = asyncio.Semaphore(5)
        total_entities, total_rels = 0, 0

        async def extract_one(chunk: Chunk):
            nonlocal total_entities, total_rels
            async with semaphore:
                result = await asyncio.to_thread(self.entity_extractor.extract, chunk.text, chunk.chunk_id)
                if result.entities:
                    await asyncio.to_thread(
                        self.graph_builder.build_from_extraction,
                        result.entities, result.relationships, doc_id, chunk.chunk_id,
                    )
                    total_entities += len(result.entities)
                    total_rels += len(result.relationships)

        await asyncio.gather(*[extract_one(c) for c in chunks])
        return total_entities, total_rels

    async def list_documents(self) -> list[DocumentMetadata]:
        return list(_document_store.values())

    async def delete_document(self, doc_id: str) -> bool:
        if doc_id not in _document_store:
            return False

        from qdrant_client.models import Filter, FieldCondition, MatchValue
        self.vector_retriever.client.delete(
            collection_name=settings.COLLECTION_NAME,
            points_selector=Filter(must=[FieldCondition(key="doc_id", match=MatchValue(value=doc_id))]),
        )
        self.graph_builder.delete_document_graph(doc_id)
        del _document_store[doc_id]
        logger.info(f"Deleted document {doc_id}")
        return True
