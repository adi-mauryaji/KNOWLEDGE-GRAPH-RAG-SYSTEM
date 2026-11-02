import pytest
from ingestion.chunker import Chunker, ChunkingStrategy
from llama_index.core import Document

class TestChunker:

    def setup_method(self):
        # Runs before EVERY test method — fresh chunker each time
        self.chunker = Chunker(
            strategy = ChunkingStrategy.RECURSIVE,
            chunk_size = 512,
            chunk_overlap = 50
        )

    def test_basic_chunking(self):
        doc = Document(text="A"*2000)
        nodes = self.chunker.chunk([doc])
        assert len(nodes) > 1
        assert all(len(node.text) <= 512*5 for node in nodes) 

    def test_metadata_preserved(self):
        doc = Document(
           text = "text_content" * 100,
           metadata = {"doc_id": "test-123", "page_label":"5"} 
        )
        nodes = self.chunker.chunk([doc])
        for node in nodes:
            assert "doc_id" in node.metadata

    def test_overlap_exists(self):
        #Adjacent chunks should share some content
        doc = Document(text = " ".join([f"sentence_{i}" for i in range(200)]))
        nodes = self.chunker.chunk([doc])

        if len(nodes) > 1:
            chunk1_words = set(nodes[0].text.split()[-20:])
            chunk2_words = set(nodes[1].text.split()[:20])
            assert len(chunk1_words & chunk2_words) > 0

    def test_empty_document(self):
        doc = Document(text="")
        nodes = self.chunker.chunk([doc])
        assert len(nodes) == 0
    

    
