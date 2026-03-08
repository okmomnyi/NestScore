import uuid
from decimal import Decimal

from sqlalchemy import (
    DECIMAL,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    plot_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("plots.id", ondelete="CASCADE"),
        nullable=False,
    )
    stars: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    comment_text: Mapped[str] = mapped_column(Text, nullable=False)
    fingerprint_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    ip_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    subnet_prefix_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    nickname: Mapped[str | None] = mapped_column(String(50), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending")
    ai_quality_score: Mapped[Decimal | None] = mapped_column(DECIMAL(3, 2), nullable=True)
    ai_toxicity_score: Mapped[Decimal | None] = mapped_column(DECIMAL(3, 2), nullable=True)
    rating_weight: Mapped[Decimal] = mapped_column(DECIMAL(3, 2), nullable=False, default=1.0)
    flag_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    disagree_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    publish_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    __table_args__ = (
        CheckConstraint("stars >= 1 AND stars <= 5", name="ck_reviews_stars"),
        CheckConstraint(
            "char_length(comment_text) >= 80 AND char_length(comment_text) <= 2000",
            name="ck_reviews_comment_length",
        ),
        UniqueConstraint("fingerprint_hash", "plot_id", name="uq_reviews_fingerprint_plot"),
        Index("ix_reviews_plot_id", "plot_id"),
        Index("ix_reviews_status", "status"),
        Index("ix_reviews_publish_at", "publish_at"),
    )
