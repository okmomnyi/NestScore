"""
FastAPI router for NestScore chatbot.
Provides /api/chat endpoint for student questions.
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
import bleach
from app.chatbot.service import ask_chatbot
from app.services.hashing import hash_ip
from app.services.rate_limiter import record_chat_submission
from app.redis_client import get_redis
from app.config import settings

router = APIRouter(prefix="/api/chat", tags=["Chatbot"])


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=2, max_length=500, description="Student question")


class ChatResponse(BaseModel):
    reply: str


@router.post("", response_model=ChatResponse)
async def chat_endpoint(body: ChatRequest, request: Request):
    """
    Ask NestScore Assistant a question.
    Rate limited to 20 questions per IP per hour.
    """
    raw_ip = request.client.host if request.client else "0.0.0.0"
    
    # Rate limit - 20 questions per IP per hour
    ip_hash = hash_ip(raw_ip, settings.IP_HASH_SALT)
    try:
        redis = await get_redis()
        allowed, retry_after = await record_chat_submission(redis, ip_hash)
        if not allowed:
            raise HTTPException(
                status_code=429,
                detail="You have asked too many questions recently. Please wait before asking again.",
                headers={"Retry-After": str(retry_after)},
            )
    except HTTPException:
        raise
    except Exception:
        pass  # Redis unavailable - skip rate limiting
    
    # Sanitize input
    clean_message = bleach.clean(body.message, tags=[], strip=True)
    
    if len(clean_message.strip()) < 2:
        raise HTTPException(status_code=400, detail="Message too short")
    
    # Get AI response
    reply = await ask_chatbot(clean_message)
    
    if not reply:
        raise HTTPException(
            status_code=503,
            detail="Chatbot service is temporarily unavailable. Please try again later."
        )
    
    return ChatResponse(reply=reply)
