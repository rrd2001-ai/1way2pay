from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from .database import Base, engine, get_db
from .models import Merchant, Payment
from .payments import create_payment, mark_payment_success
from .webhooks import create_webhook_event, deliver_webhook
from .schemas import PaymentCreate

from .auth import get_current_merchant

Base.metadata.create_all(bind=engine)

def create_test_merchant():
    db = next(get_db())

    existing = (
        db.query(Merchant)
        .filter(Merchant.api_key == "nw_test_123456")
        .first()
    )

    if not existing:
        merchant = Merchant(
            id="merchant_test_001",
            name="Test Merchant",
            api_key="nw_test_123456",
        )

        db.add(merchant)
        db.commit()

    db.close()


create_test_merchant()

app = FastAPI(
    title="1Way2Pay API",
    description="Payment infrastructure API",
    version="0.1.0",
)

@app.get("/")
def root():
    return {
        "name": "1Way2Pay",
        "version": "0.1.0",
        "status": "running",
    }

@app.post("/v1/payments")
def create_payment_endpoint(
    payment_data: PaymentCreate,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
    db: Session = Depends(get_db),
    merchant: Merchant = Depends(get_current_merchant),
):
    existing_payment = (
        db.query(Payment)
        .filter(
            Payment.merchant_id == merchant.id,
            Payment.idempotency_key == idempotency_key,
        )
        .first()
    )

    if existing_payment:
        if (
            existing_payment.amount != payment_data.amount
            or existing_payment.currency != payment_data.currency
            or existing_payment.order_id != payment_data.order_id
        ):
            raise HTTPException(
                status_code=409,
                detail="Idempotency key already used with different payment details",
            )

        return {
            "id": existing_payment.id,
            "amount": existing_payment.amount,
            "currency": existing_payment.currency,
            "order_id": existing_payment.order_id,
            "status": existing_payment.status,
            "checkout_url": f"/pay/{existing_payment.id}",
        }

    payment = create_payment(
        db=db,
        amount=payment_data.amount,
        currency=payment_data.currency,
        order_id=payment_data.order_id,
        merchant=merchant,
        idempotency_key=idempotency_key,
    )

    return {
        "id": payment.id,
        "amount": payment.amount,
        "currency": payment.currency,
        "order_id": payment.order_id,
        "status": payment.status,
        "checkout_url": f"/pay/{payment.id}",
    }

@app.get("/v1/payments/{payment_id}")
def get_payment(
    payment_id: str,
    db: Session = Depends(get_db),
    merchant: Merchant = Depends(get_current_merchant),
):
    payment = (
    db.query(Payment)
    .filter(
        Payment.id == payment_id,
        Payment.merchant_id == merchant.id,
    )
    .first()
)

    if not payment:
        raise HTTPException(
            status_code=404,
            detail="Payment not found",
        )

    return {
        "id": payment.id,
        "amount": payment.amount,
        "currency": payment.currency,
        "order_id": payment.order_id,
        "status": payment.status,
        "provider": payment.provider,
        "provider_transaction_id": payment.provider_transaction_id,
    }


@app.get("/pay/{payment_id}")
def checkout(
    payment_id: str,
    db: Session = Depends(get_db),
):
    payment = (
        db.query(Payment)
        .filter(Payment.id == payment_id)
        .first()
    )

    if not payment:
        raise HTTPException(
            status_code=404,
            detail="Payment not found",
        )

    if payment.status == "success":
        raise HTTPException(
            status_code=400,
            detail="Payment already completed",
        )

    return FileResponse("static/checkout.html")

@app.post("/v1/payments/{payment_id}/simulate-success")
def simulate_success(
    payment_id: str,
    db: Session = Depends(get_db),
    merchant: Merchant = Depends(get_current_merchant),
):
    payment = (
        db.query(Payment)
        .filter(
            Payment.id == payment_id,
            Payment.merchant_id == merchant.id,
        )
        .first()
    )

    if not payment:
        raise HTTPException(
            status_code=404,
            detail="Payment not found",
        )

    if payment.status == "success":
        return {
            "message": "Payment already successful",
            "payment_id": payment.id,
            "status": payment.status,
        }

    payment = mark_payment_success(db, payment)

    event = create_webhook_event(
    db=db,
    payment=payment,
)

    event = deliver_webhook(
        db=db,
        event=event,
        merchant=merchant,
        payment=payment,
    )

    return {
        "message": "Payment successful",
        "payment_id": payment.id,
        "status": payment.status,
        "provider_transaction_id": payment.provider_transaction_id,
        "webhook_event_id": event.id,
        "webhook_event_type": event.event_type,
        "webhook_status": event.status,
        "webhook_attempts": event.attempts,
    }