import uuid
from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field


class AdminReviewAction(BaseModel):
    note: str | None = None


class AdminPlotCreate(BaseModel):
    name: str = Field(..., max_length=200)
    area: str = Field(..., max_length=100)
    description: str
    gps_lat: Decimal = Field(..., ge=-90, le=90)
    gps_lng: Decimal = Field(..., ge=-180, le=180)


class AdminPlotUpdate(BaseModel):
    name: str | None = Field(None, max_length=200)
    area: str | None = Field(None, max_length=100)
    description: str | None = None
    gps_lat: Decimal | None = Field(None, ge=-90, le=90)
    gps_lng: Decimal | None = Field(None, ge=-180, le=180)


class AdminDisputeAction(BaseModel):
    admin_note: str | None = None


class AdminSuggestionResponse(BaseModel):
    id: uuid.UUID
    suggested_name: str
    area: str
    notes: str | None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class AuditLogResponse(BaseModel):
    id: uuid.UUID
    admin_action: str
    target_type: str
    target_id: uuid.UUID
    note: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class AdminLoginRequest(BaseModel):
    password: str
