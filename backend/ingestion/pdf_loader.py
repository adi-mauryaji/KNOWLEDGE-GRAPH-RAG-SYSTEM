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