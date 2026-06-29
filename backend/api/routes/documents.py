from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from services.ingestion_service import IngestionService
from models.chat import DocumentUploadResponse
import uuid

router = APIRouter()

def get_ingestion_service() -> IngestionService:
    return IngestionService()

@router.post("/upload",response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    service: IngestionService = Depends(get_ingestion_service)
):
    
    # Validation --Jo sari mangti hain
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400,detail='Only PDF files accepted')
    
    if file.size > 50*1024*1024:
        raise HTTPException(status_code=413, detail="File too large. Max 50MB")
    
    doc_id = str(uuid.uuid4())

    try:
        result = await service.process_document(
            file=file,
            doc_id=doc_id
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"processing failed: {str(e)}")
    
@router.delete("/document/{doc_id}")
async def delete_document(
    doc_id = str,
    service: IngestionService = Depends(get_ingestion_service)
):
    
    success = await service.delete_document(doc_id)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"status":"deleted", "doc_id":doc_id}