import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class ReviewSubmit(BaseModel):
    plot_id: uuid.UUID
    stars: int = Field(..., ge=1, le=5)
    comment_text: str = Field(..., min_length=80, max_length=2000)
    fingerprint_hash: str = Field(..., min_length=1, max_length=128)
    turnstile_token: str


class ReviewSubmitResponse(BaseModel):
    id: uuid.UUID
    publish_at: datetime
    message: str = "Your review has been submitted and will be published within 20 minutes."


class ReviewPublicResponse(BaseModel):
    id: uuid.UUID
    stars: int
    comment_text: str
    nickname: str | None = None
    status: str
    flag_count: int
    disagree_count: int
    publish_at: datetime
    created_at: datetime
    dispute_response: str | None = None

    model_config = {"from_attributes": True}


class FlagSubmit(BaseModel):
    reason: str = Field(..., pattern="^(offensive|spam|false_claim|disagree_vote|other)$")
    fingerprint_hash: str = Field(..., min_length=1, max_length=128)


class ReviewListResponse(BaseModel):
    reviews: list[ReviewPublicResponse]
    total_count: int
    page: int
    per_page: int


class ReviewAdminResponse(BaseModel):
    id: uuid.UUID
    plot_id: uuid.UUID
    stars: int
    comment_text: str
    nickname: str | None
    status: str
    flag_count: int
    ai_quality_score: Decimal | None
    ai_toxicity_score: Decimal | None
    publish_at: datetime
    created_at: datetime
    disagree_count: int

    model_config = {"from_attributes": True}
