from llama_index.core import SimpleDirectoryReader, Document
import hashlib
from pathlib import Path
from utils.logger import get_logger

logger = get_logger(__name__)

class PDFLoader:
    def __init__(self, file_path: str, doc_id: str ) -> list[Document]:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        logger.info(f"Loading PDF: {path.name}")

        reader = SimpleDirectoryReader(
            input_files=[str(file_path)],
            filename_as_id=True,
            required_exts=[".pdf"]
        )

        documents = reader.load_data()

        # Enrich metadata
        for doc in documents:
            doc.metadata.update({
                "doc_id": doc_id,
                "file_hash": self._compute_hash(file_path),
                "total_pages": len(documents)
            })

        logger.info(f"Loaded {len(documents)} pages from {path.name}")
        return documents
    
    def _compute_hash(self, file_path: str) -> str:            # md5 hash for duplicate detection jaise bhandare me ek hota hai phechanne wala
        with open(file_path, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()