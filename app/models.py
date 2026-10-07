from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, UniqueConstraint
from .database import Base


class Payment(Base):
    __tablename__ = "payments"
    __table_args__ = (
    UniqueConstraint(
        "merchant_id",
        "idempotency_key",
        name="uq_payment_merchant_idempotency",
    ),
)
    id = Column(String, primary_key=True, index=True)

    merchant_id = Column(
        String,
        ForeignKey("merchants.id"),
        nullable=True,
        index=True,
    )

    idempotency_key = Column(String, nullable=True, index=True)

    order_id = Column(String, nullable=False, index=True)

    amount = Column(Integer, nullable=False)
    currency = Column(String, nullable=False, default="INR")

    status = Column(String, nullable=False, default="created")

    provider = Column(String, nullable=False, default="mock_bank")
    provider_transaction_id = Column(String, nullable=True)

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
    )

    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

class Merchant(Base):
    __tablename__ = "merchants"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    api_key = Column(String, nullable=False, unique=True, index=True)
    webhook_url = Column(String, nullable=True)
    webhook_secret = Column(String, nullable=True)
    
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
    )

class WebhookEvent(Base):
    __tablename__ = "webhook_events"

    id = Column(String, primary_key=True, index=True)

    merchant_id = Column(
        String,
        ForeignKey("merchants.id"),
        nullable=False,
        index=True,
    )

    payment_id = Column(
        String,
        ForeignKey("payments.id"),
        nullable=False,
        index=True,
    )

    event_type = Column(String, nullable=False)

    status = Column(
        String,
        nullable=False,
        default="pending",
    )

    attempts = Column(
        Integer,
        nullable=False,
        default=0,
    )

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
    )

    delivered_at = Column(
        DateTime,
        nullable=True,
    )