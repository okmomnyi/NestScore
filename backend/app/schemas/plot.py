import uuid
from decimal import Decimal

from pydantic import BaseModel, Field


class PlotBase(BaseModel):
    name: str = Field(..., max_length=200)
    area: str = Field(..., max_length=100)
    description: str
    gps_lat: Decimal = Field(..., ge=-90, le=90)
    gps_lng: Decimal = Field(..., ge=-180, le=180)


class PlotCreate(PlotBase):
    pass


class PlotUpdate(BaseModel):
    name: str | None = Field(None, max_length=200)
    area: str | None = Field(None, max_length=100)
    description: str | None = None
    gps_lat: Decimal | None = Field(None, ge=-90, le=90)
    gps_lng: Decimal | None = Field(None, ge=-180, le=180)


class PlotResponse(PlotBase):
    id: uuid.UUID
    weighted_score: Decimal | None
    raw_avg: Decimal | None
    total_ratings: int
    status: str
    landlord_claimed: bool

    model_config = {"from_attributes": True}


class PlotMapResponse(BaseModel):
    id: uuid.UUID
    name: str
    area: str
    gps_lat: Decimal
    gps_lng: Decimal
    weighted_score: Decimal | None
    total_ratings: int
    status: str

    model_config = {"from_attributes": True}


class PlotListResponse(BaseModel):
    plots: list[PlotResponse]
    total_count: int
    page: int
    per_page: int
