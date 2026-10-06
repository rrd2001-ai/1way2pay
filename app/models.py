from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from .database import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(String, primary_key=True, index=True)

    merchant_id = Column(
        String,
        ForeignKey("merchants.id"),
        nullable=True,
        index=True,
    )
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

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
    )