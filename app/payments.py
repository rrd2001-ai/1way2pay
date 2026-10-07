import uuid

from sqlalchemy.orm import Session

from .models import Merchant, Payment


VALID_TRANSITIONS = {
    "created": {"processing", "failed", "expired"},
    "processing": {"success", "failed", "expired"},
    "success": set(),
    "failed": set(),
    "expired": set(),
}


def create_payment(
    db: Session,
    amount: int,
    currency: str,
    order_id: str,
    merchant: Merchant,
    idempotency_key: str,
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
        idempotency_key=idempotency_key,
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    return payment


def transition_payment(
    db: Session,
    payment: Payment,
    new_status: str,
) -> Payment:

    allowed_statuses = VALID_TRANSITIONS.get(
        payment.status,
        set(),
    )

    if new_status not in allowed_statuses:
        raise ValueError(
            f"Invalid payment transition: "
            f"{payment.status} -> {new_status}"
        )

    payment.status = new_status

    if new_status == "success":
        payment.provider_transaction_id = (
            f"mock_txn_{uuid.uuid4().hex[:12]}"
        )

    db.commit()
    db.refresh(payment)

    return payment


def mark_payment_processing(
    db: Session,
    payment: Payment,
) -> Payment:

    return transition_payment(
        db,
        payment,
        "processing",
    )


def mark_payment_success(
    db: Session,
    payment: Payment,
) -> Payment:

    return transition_payment(
        db,
        payment,
        "success",
    )


def mark_payment_failed(
    db: Session,
    payment: Payment,
) -> Payment:

    return transition_payment(
        db,
        payment,
        "failed",
    )


def mark_payment_expired(
    db: Session,
    payment: Payment,
) -> Payment:

    return transition_payment(
        db,
        payment,
        "expired",
    )