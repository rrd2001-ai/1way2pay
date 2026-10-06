from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String

from .database import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(String, primary_key=True, index=True)
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