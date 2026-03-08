import uuid
from decimal import Decimal

from sqlalchemy import (
    DECIMAL,
    Boolean,
    DateTime,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Plot(Base):
    __tablename__ = "plots"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    area: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    gps_lat: Mapped[Decimal] = mapped_column(DECIMAL(10, 8), nullable=False)
    gps_lng: Mapped[Decimal] = mapped_column(DECIMAL(11, 8), nullable=False)
    weighted_score: Mapped[Decimal | None] = mapped_column(DECIMAL(3, 2), nullable=True, default=None)
    raw_avg: Mapped[Decimal | None] = mapped_column(DECIMAL(3, 2), nullable=True, default=None)
    total_ratings: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    landlord_claimed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    claim_verified_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    # Anomaly detection fields
    last_score_snapshot: Mapped[Decimal | None] = mapped_column(DECIMAL(3, 2), nullable=True)
    last_snapshot_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        Index("ix_plots_area", "area"),
        Index("ix_plots_status", "status"),
        Index("ix_plots_weighted_score", "weighted_score"),
    )
