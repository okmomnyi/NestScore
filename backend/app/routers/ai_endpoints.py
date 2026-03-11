"""AI-powered endpoints for intelligent content generation."""
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.database import get_db
from app.models.plot import Plot
from app.models.review import Review
from app.services.ai_service import ai_service

router = APIRouter(prefix="/api/ai", tags=["AI"])


class GenerateDescriptionRequest(BaseModel):
    plot_name: str
    area: str


class AnalyzeReviewRequest(BaseModel):
    review_text: str


class SummarizeReviewsRequest(BaseModel):
    plot_id: uuid.UUID


class GenerateWelcomeRequest(BaseModel):
    context: str = ""


@router.post("/generate-description")
async def generate_plot_description(body: GenerateDescriptionRequest):
    """Generate AI description for a plot."""
    if not ai_service.enabled:
        raise HTTPException(status_code=503, detail="AI service not configured")
    
    description = await ai_service.generate_plot_description(
        plot_name=body.plot_name,
        area=body.area
    )
    
    return {
        "description": description,
        "ai_generated": True
    }


@router.post("/analyze-review")
async def analyze_review(body: AnalyzeReviewRequest):
    """Analyze sentiment and key points from a review."""
    if not ai_service.enabled:
        raise HTTPException(status_code=503, detail="AI service not configured")
    
    analysis = await ai_service.analyze_review_sentiment(body.review_text)
    
    return analysis


@router.post("/summarize-reviews")
async def summarize_plot_reviews(
    body: SummarizeReviewsRequest,
    db: AsyncSession = Depends(get_db)
):
    """Generate AI summary of all reviews for a plot."""
    if not ai_service.enabled:
        raise HTTPException(status_code=503, detail="AI service not configured")
    
    # Fetch active reviews for the plot
    result = await db.execute(
        select(Review.comment_text)
        .where(Review.plot_id == body.plot_id, Review.status == "active")
        .limit(10)
    )
    reviews = [row[0] for row in result.all()]
    
    if not reviews:
        return {"summary": "No reviews available for this plot.", "ai_generated": False}
    
    summary = await ai_service.summarize_reviews(reviews)
    
    return {
        "summary": summary,
        "review_count": len(reviews),
        "ai_generated": True
    }


@router.post("/welcome-message")
async def generate_welcome_message(body: GenerateWelcomeRequest):
    """Generate a personalized welcome message."""
    if not ai_service.enabled:
        return {
            "message": "Welcome to NestScore! Find honest reviews of rental plots.",
            "ai_generated": False
        }
    
    message = await ai_service.generate_welcome_message(body.context)
    
    return {
        "message": message,
        "ai_generated": True
    }


@router.get("/status")
async def ai_service_status():
    """Check if AI service is available."""
    return {
        "enabled": ai_service.enabled,
        "model": ai_service.model if ai_service.enabled else None,
        "status": "operational" if ai_service.enabled else "disabled"
    }
