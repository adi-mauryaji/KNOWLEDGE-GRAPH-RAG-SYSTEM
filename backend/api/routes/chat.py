from fastapi import APIRouter, HTTPException, Depends
from services.chat_service import ChatService
from models.chat import ChatRequest, ChatResponse
import time, uuid

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    sevice: ChatService = Depends(ChatService)
):
    
    start_time = time.time()

    if not request.query.strip():
        raise HTTPException(status_code = 400, detail = "query cannot be empty")
    
    try:
        answer, citations = await service.answer_query(
            query = request.query,
            doc_ids = request.doc_ids,
            top_k = request.top_k
        )

        processing_time = int((time.time()-start_time)*1000)

        return ChatResponse(
            answer = answer,
            citations = citations,
            query_id = str(uuid.uuid4()),
            processing_time_ms = processing_time,
            sources_used = list(set(c.filename for c in citations)),
            chunks_retrieved = len(citations)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))