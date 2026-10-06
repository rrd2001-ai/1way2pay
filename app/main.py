from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from .database import Base, engine, get_db
from .models import Payment
from .payments import create_payment, mark_payment_success
from .schemas import PaymentCreate

Base.metadata.create_all(bind=engine)

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
    db: Session = Depends(get_db),
):
    payment = create_payment(
        db=db,
        amount=payment_data.amount,
        currency=payment_data.currency,
        order_id=payment_data.order_id,
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
        return {
            "message": "Payment already successful",
            "payment_id": payment.id,
            "status": payment.status,
        }

    payment = mark_payment_success(db, payment)

    return {
        "message": "Payment successful",
        "payment_id": payment.id,
        "status": payment.status,
        "provider_transaction_id": payment.provider_transaction_id,
    }