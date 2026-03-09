import uuid
from decimal import Decimal
from sqlalchemy import DECIMAL, DateTime, Index, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class PlotSuggestion(Base):
    __tablename__ = "plot_suggestions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    area: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    gps_lat: Mapped[Decimal | None] = mapped_column(DECIMAL(10, 8), nullable=True)
    gps_lng: Mapped[Decimal | None] = mapped_column(DECIMAL(11, 8), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    submitter_ip: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index("ix_plot_suggestions_status", "status"),
        Index("ix_plot_suggestions_created_at", "created_at"),
    )
