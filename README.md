# Knowledge Graph RAG System

Upload PDFs and ask questions about them. The system searches a vector database and a knowledge graph together, then answers with citations to the source documents.

## Features

- **PDF ingestion:** parses, cleans and chunks uploaded PDFs.
- **Vector search:** stores chunk embeddings in Qdrant.
- **Knowledge graph:** an LLM extracts entities and relationships from each chunk and stores them in Neo4j.
- **Hybrid retrieval:** runs vector and graph search in parallel, then merges and reranks the results.
- **Cited answers:** generates answers with Gemini or OpenAI and links them back to their sources.
- **Graph view:** explores the extracted entities and relationships in an interactive Streamlit page.
- **Local embeddings:** can use BGE embeddings on your own machine, with no embedding API costs.

## How it works

```text
                   +-------------------+
   Browser ------> | Streamlit  :8501  |
                   +---------+---------+
                             | HTTP
                   +---------v---------+
                   | FastAPI    :8000  | ------> Gemini or OpenAI
                   +----+---------+----+
                        |         |
           +------------v--+   +--v------------+
           | Qdrant  :6333 |   | Neo4j   :7687 |
           | chunks and    |   | entities and  |
           | embeddings    |   | relationships |
           +---------------+   +---------------+
```

**When you upload a PDF:**

1. The text is extracted, cleaned and split into chunks.
2. Each chunk is embedded and stored in Qdrant.
3. An LLM extracts entities and relationships from each chunk, and these are stored in Neo4j.

**When you ask a question:**

1. Qdrant and Neo4j are searched in parallel.
2. The results are merged, deduplicated and reranked.
3. The top chunks are sent to the LLM as context.
4. The answer is returned with citations.

## Tech stack

| Area | Tools |
|---|---|
| API | FastAPI, Uvicorn |
| Frontend | Streamlit, pyvis |
| Document processing | LlamaIndex, pypdf |
| Vector database | Qdrant |
| Graph database | Neo4j 5.15 Community |
| LLM | Gemini or OpenAI |
| Embeddings | BGE (sentence-transformers), OpenAI or Gemini |
| Tests | pytest |

## Prerequisites

- Python 3.12
- Docker
- A [Gemini API key](https://aistudio.google.com/apikey) or a paid OpenAI API key
- About 7 GB of free disk space for the Python packages, because the install includes PyTorch

## Setup

### 1. Get the code and install dependencies

```bash
git clone https://github.com/adi-mauryaji/KNOWLEDGE-GRAPH-RAG-SYSTEM.git
cd KNOWLEDGE-GRAPH-RAG-SYSTEM

python3.12 -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate

pip install -r backend/requirements.txt -r frontend/requirements.txt
```

### 2. Create the `.env` file

```bash
cp .env.example .env
```

Open `.env` and set the lines below. Replace a line if it already exists, and add it if it doesn't.

**Option A: Gemini with local BGE embeddings**

```bash
GEMINI_API_KEY=your-gemini-key
NEO4J_PASSWORD=choose-a-password
LLM_PROVIDER=gemini
EMBEDDING_PROVIDER=bge
EMBEDDING_DIMENSION=384
COLLECTION_NAME=documents_bge
GEMINI_CHAT_MODEL=gemini-3.8-flash
```

Gemini has a free tier, but Google may use free-tier data to improve its products, so don't upload confidential documents on it. The BGE model (about 130 MB) downloads the first time it's used.

**Option B: OpenAI (paid)**

```bash
OPENAI_API_KEY=your-openai-key
NEO4J_PASSWORD=choose-a-password
LLM_PROVIDER=openai
EMBEDDING_PROVIDER=openai
```

Keep `.env` in the project root. Git ignores it, so your keys stay out of the repository.

### 3. Create the database containers

Run this once. Use the same `NEO4J_PASSWORD` you set in `.env`. It must be at least 8 characters long.

```bash
docker run -d --name kg-rag-qdrant \
  -p 6333:6333 -p 6334:6334 \
  -v qdrant_storage:/qdrant/storage \
  qdrant/qdrant

docker run -d --name kg-rag-neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/choose-a-password \
  -v neo4j_data:/data -v neo4j_logs:/logs \
  neo4j:5.15-community
```

## Run the project

**1. Start the databases.** Skip this right after creating the containers, because they're already running.

```bash
docker start kg-rag-qdrant kg-rag-neo4j
```

Neo4j can take around 30 seconds to become ready.

**2. Start the backend in a new terminal.** Run it from `backend/`.

```bash
source .venv/bin/activate
cd backend
uvicorn main:app --reload
```

**3. Start the frontend in a second terminal.** Run it from `frontend/`.

```bash
source .venv/bin/activate
cd frontend
streamlit run app.py
```

**4. Open the app.**

| Service | URL |
|---|---|
| Web app | http://localhost:8501 |
| API docs | http://localhost:8000/docs |
| Backend health check | http://localhost:8000/health |
| Neo4j Browser | http://localhost:7474 |
| Qdrant dashboard | http://localhost:6333/dashboard |

**To stop the project:** press `Ctrl+C` in both terminals, then run:

```bash
docker stop kg-rag-qdrant kg-rag-neo4j
```

Your data stays in the Docker volumes.

## Using the app

1. **Upload:** add a PDF and wait for processing to finish. Large PDFs take longer because each chunk needs its own LLM call.
2. **Chat:** ask a question about your documents and check the citations under the answer.
3. **Graph:** generate an interactive view of the extracted entities and relationships.

## API

The base URL is `http://localhost:8000`. Full request and response details are at `/docs`.

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Checks that the backend is running |
| `POST` | `/api/v1/upload` | Uploads and processes a PDF (form field: `file`) |
| `GET` | `/api/v1/documents` | Lists processed documents |
| `DELETE` | `/api/v1/document/{doc_id}` | Deletes a document and its data |
| `POST` | `/api/v1/chat` | Answers a question with citations |
| `GET` | `/api/v1/graph` | Returns graph data (optional: `doc_id`, `entity_type`, `limit`) |

```bash
curl -X POST http://localhost:8000/api/v1/upload -F "file=@paper.pdf"

curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the main contribution of this paper?", "top_k": 5}'
```

In a chat request, `query` can be up to 500 characters, `top_k` can be 1 to 20 (default 5), and an optional `doc_ids` list limits the search to specific documents.

## Configuration

Settings are read from `.env`. These are the ones you're most likely to change:

| Setting | Default | Purpose |
|---|---|---|
| `LLM_PROVIDER` | `openai` | `openai` or `gemini` |
| `EMBEDDING_PROVIDER` | `openai` | `openai`, `bge` or `gemini` |
| `EMBEDDING_DIMENSION` | `1536` | Vector size, which is 384 for the default BGE model |
| `COLLECTION_NAME` | `documents` | Qdrant collection name |
| `GEMINI_API_KEY` | empty | Needed for Gemini |
| `GEMINI_CHAT_MODEL` | `gemini-1.5-flash` | This default has been retired, so set a current model |
| `OPENAI_API_KEY` | empty | Needed for OpenAI |
| `OPENAI_CHAT_MODEL` | `gpt-4o-mini` | OpenAI model for answers |
| `EXTRACTION_MODEL` | `gpt-4o-mini` | OpenAI model for entity extraction |
| `NEO4J_PASSWORD` | `password` | Must match the Neo4j container |
| `CHUNK_SIZE` | `512` | Chunk size |
| `CHUNK_OVERLAP` | `50` | Overlap between chunks |
| `SKIP_EXTRACTION` | `false` | Skips the graph step, so uploads make no LLM calls |
| `UPLOAD_DIR` | `/app/uploads` | Where PDFs are saved. Use `uploads` when running locally |

The frontend reads one setting from its environment: `BACKEND_API_URL`, which defaults to `http://localhost:8000/api/v1`.

**If you change the embedding model:** existing vectors won't match the new size, and the backend will refuse to start. Set a new `COLLECTION_NAME`, or delete the old collection, and upload your documents again.

## Tests

```bash
source .venv/bin/activate
cd backend
python -m pytest tests/unit -q
```

The unit tests don't need Docker or API keys.

## Project structure

```text
.
├── backend/
│   ├── main.py             # FastAPI app and startup connections
│   ├── api/routes/         # Upload, document, chat and graph endpoints
│   ├── services/           # Ingestion, chat and citation logic
│   ├── ingestion/          # PDF loading, text cleaning, chunking
│   ├── embeddings/         # OpenAI, BGE and Gemini embedders
│   ├── vector_store/       # Qdrant client and vector search
│   ├── graph/              # Neo4j client, entity extraction, graph building and search
│   ├── retrieval/          # Hybrid retrieval, reranking, context building
│   ├── llm/                # Gemini and OpenAI clients, prompts
│   ├── models/             # Pydantic models
│   ├── utils/              # Settings and logging
│   └── tests/unit/         # Unit tests
├── frontend/
│   ├── app.py              # Streamlit home page
│   ├── pages/              # Upload, Chat and Graph pages
│   ├── components/         # Citation display and graph view
│   └── utils/api_client.py # Calls to the backend
└── .env.example            # Configuration template
```

## Troubleshooting

| Problem | Fix |
|---|---|
| `Router.__init__() got an unexpected keyword argument 'on_startup'` | A package version doesn't match the pinned one. Activate the virtual environment and run the `pip install` command again. |
| `ValidationError` for `LLM_PROVIDER` or `EMBEDDING_PROVIDER` | The line in `.env` still has extra text after the value. Replace it as shown in [Create the `.env` file](#2-create-the-env-file). |
| Connection error when the backend starts | Run `docker ps` to check that both containers are up. If Neo4j just started, wait about 30 seconds and try again. |
| Neo4j `Unauthorized` error | `NEO4J_PASSWORD` doesn't match the password the Neo4j data volume was created with. Changing `NEO4J_AUTH` later doesn't update an existing volume. |
| Neo4j can't create `entity_name_unique` | The existing graph has duplicate entity names. Run `MATCH (e:Entity) DETACH DELETE e` in Neo4j Browser, which deletes all entities, then restart the backend and upload your documents again. |
| `RuntimeError` about the collection dimension | The embedding model changed. See [Configuration](#configuration). |
| Gemini model error | Set `GEMINI_CHAT_MODEL` in `.env` to a model that's currently available. |
| Connection error on a Streamlit page | Make sure the backend is running. If it's on another address, set `BACKEND_API_URL`. |

## Known limitations

- **PDF only, no OCR:** only `.pdf` files are accepted, and scanned PDFs won't produce usable text.
- **No authentication:** the API is open to anyone who can reach it, so run it only on your own machine.
- **Document list is kept in memory:** it's empty after a backend restart, and those documents can't be deleted through the API, even though their data is still in Qdrant and Neo4j.
- **Rate limits:** extraction makes one LLM call per chunk, up to five at a time. Large PDFs can hit free-tier limits, which can leave some chunks out of the graph.
- **No upload size limit:** `MAX_FILE_SIZE_MB` is defined but not enforced.
- **Unused settings:** `USE_POSTGRES`, `POSTGRES_URL`, `MIN_RELEVANCE_SCORE`, `VECTOR_WEIGHT`, `DEFAULT_TOP_K` and `DEBUG` currently have no effect, and neither does `vector_weight` in chat requests.
