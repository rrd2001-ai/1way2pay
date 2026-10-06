import uuid
from sqlalchemy.orm import Session
from .models import Merchant, Payment


def create_payment(
    db: Session,
    amount: int,
    currency: str,
    order_id: str,
    merchant: Merchant,
) -> Payment:

    payment_id = f"pay_{uuid.uuid4().hex[:12]}"

    payment = Payment(
        id=payment_id,
        merchant_id=merchant.id,
        amount=amount,
        currency=currency,
        order_id=order_id,
        status="created",
        provider="mock_bank",
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    return payment


def mark_payment_success(
    db: Session,
    payment: Payment,
) -> Payment:

    payment.status = "success"
    payment.provider_transaction_id = (
        f"mock_txn_{uuid.uuid4().hex[:12]}"
    )

    db.commit()
    db.refresh(payment)

    return payment