import os
import httpx

API_BASE = os.getenv("BACKEND_API_URL", "http://localhost:8000/api/v1")

class APIClient:
    def __init__(self):
        self.base = API_BASE


    def upload_document(self, file_bytes: bytes, filename: str) -> dict:
        with httpx.Client(timeout = 120) as client:
            response = client.post(
                f"{self.base}/upload",
                files = {"file": (filename, file_bytes, "application/pdf")}
            )
            response.raise_for_status()
            return response.json()

    def chat(self, query: str, doc_ids: list = None, top_k: int = 5) -> dict:
        with httpx.Client(timeout = 60) as client:
            response = client.post(
                f"{self.base}/chat",
                json = {
                    "query": query,
                    "doc_ids": doc_ids,
                    "top_k": top_k
                }
            )
            response.raise_for_status()
            return response.json()

    def get_documents(self) -> list:
        with httpx.Client(timeout=30) as client:
            response = client.get(f"{self.base}/documents")
            response.raise_for_status()
            return response.json()

    def get_graph(self, doc_id: str = None) -> dict:
        params = {"doc_id": doc_id} if doc_id else {}
        with httpx.Client(timeout=30) as client:
            response = client.get(f"{self.base}/graph", params=params)
            response.raise_for_status()
            return response.json()

    def health_check(self) -> bool:
        try:
            with httpx.Client(timeout=5) as client:
                response = client.get(f"{self.base.replace('/api/v1', '')}/health")
                return response.status_code == 200
        except httpx.RequestError:
            return False

    

