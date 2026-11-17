from fastapi import APIRouter, Depends, HTTPException
from app.dependencies import verify_api_key
from app.models.schemas import ChatRequest, ChatResponse
from app.services import bedrock_service

router = APIRouter(prefix="/ai", tags=["AI"], dependencies=[Depends(verify_api_key)])


@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    try:
        reply, tokens = bedrock_service.chat(req.message, context=req.context)
        return ChatResponse(reply=reply, tokens_used=tokens)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
