from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from api.routes import documents, chat, graph
from utils.config import get_settings
from vector_store.qdrant_client import init_qdrant
from graph.neo4j_client import init_neo4j

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_qdrant()
    init_neo4j()
    print("💚 All connections are initialized")
    yield
    print("😒 Bas itta hi kaam tha -\n  -------Shutting down .......")

app = FastAPI(
    title="Knowledge Graph Rag Assistant",
    description="Hybrid RAG system with Knowledge Graph",
    version = "1.0.0",
    lifespan=lifespan
)

# CORS - frontend aur backend ki guchu guchu ke liye
app.add.middleware(
    CORSMiddleware,
    allow_origins=["https://localhost:8501"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Register routers
app.include_router(documents.router,prefix="/api/v1",tags=["Documents"])
app.include_router(chat.router,prefix="/api/v1",tags=["Chat"])
app.include_router(graph.router,prefix="/api/v1",tags=["Graph"])

@app.get("/health")
async def health_check():
    return {"status":"healthy","version":"1.0.0"}