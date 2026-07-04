from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.schema import Document, TextNode
from enum import Enum

class ChunkingStrategy(Enum):
    RECURSIVE = "recursive"
    SEMENTIC = "semantic"
    SENTENCE = "sentence"

class Chunker:

    def __init__(
            self,
            strategy: ChunkingStrategy = ChunkingStrategy.RECURSIVE,
            chunk_size: int = 512,
            chunk_overlap: int = 50,
    ):
        self.strategy = strategy
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk(self, documents: list[Document]) -> list[TextNode]:
        if self.strategy == ChunkingStrategy.RECURSIVE:
            return self._recursive_chunk(documents)
        elif self.strategy == ChunkingStrategy.SENTENCE:
            return self._sentence_chunk(documents)
        else:
            raise ValueError(f"Unknown strategy: {self.strategy}")
        
    def _recursive_chunk(self, documents: list[Document]) -> list[TextNode]:
        splitter = SentenceSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            paragraph_separator="\n\n",
        )

        nodes = splitter.get_nodes_from_documents(documents)

        for i, node in enumerate(nodes):
            node.metadata["chunk_index"] = i
            node.metadata["chunk_total"] = len(nodes)

        return nodes
    
    def _sentence_chunk(self, documents: list[Document]) -> list[TextNode]:
        splitter = SentenceSplitter(chunk_size=256, chunk_overlap=20)
        return splitter.get_nodes_from_documents(documents)
    