import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class LandlordClaimRequest(BaseModel):
    plot_id: uuid.UUID
    contact_email: EmailStr


class LandlordClaimResponse(BaseModel):
    message: str = (
        "A verification email has been sent. "
        "Please check your inbox and follow the instructions to complete your claim."
    )


class DisputeSubmit(BaseModel):
    plot_id: uuid.UUID
    review_id: uuid.UUID
    landlord_response_text: str = Field(..., min_length=10, max_length=500)


class DisputeResponse(BaseModel):
    id: uuid.UUID
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ContactForm(BaseModel):
    subject: str = Field(..., max_length=100)
    message: str = Field(..., min_length=20, max_length=2000)
    turnstile_token: str
