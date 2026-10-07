from datetime import datetime, timezone
import hashlib
import hmac
import json
import uuid

import requests
from sqlalchemy.orm import Session

from .models import Merchant, Payment, WebhookEvent


def create_webhook_event(
    db: Session,
    payment: Payment,
) -> WebhookEvent:

    event = WebhookEvent(
        id=f"evt_{uuid.uuid4().hex[:12]}",
        merchant_id=payment.merchant_id,
        payment_id=payment.id,
        event_type="payment.succeeded",
        status="pending",
        attempts=0,
    )

    db.add(event)
    db.commit()
    db.refresh(event)

    return event


def generate_signature(
    payload: dict,
    secret: str,
) -> str:

    payload_bytes = json.dumps(
        payload,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")

    signature = hmac.new(
        secret.encode("utf-8"),
        payload_bytes,
        hashlib.sha256,
    ).hexdigest()

    return f"sha256={signature}"


def deliver_webhook(
    db: Session,
    event: WebhookEvent,
    merchant: Merchant,
    payment: Payment,
) -> WebhookEvent:

    if event.status == "delivered":
        return event

    if not merchant.webhook_url:
        event.status = "failed"
        db.commit()
        db.refresh(event)
        return event

    if not merchant.webhook_secret:
        event.status = "failed"
        db.commit()
        db.refresh(event)
        return event

    payload = {
        "id": event.id,
        "event": event.event_type,
        "payment_id": payment.id,
        "order_id": payment.order_id,
        "amount": payment.amount,
        "currency": payment.currency,
        "status": payment.status,
    }

    signature = generate_signature(
        payload=payload,
        secret=merchant.webhook_secret,
    )

    event.attempts += 1

    try:
        response = requests.post(
            merchant.webhook_url,
            json=payload,
            headers={
                "X-1Way2Pay-Signature": signature,
            },
            timeout=5,
        )

        if 200 <= response.status_code < 300:
            event.status = "delivered"
            event.delivered_at = datetime.now(timezone.utc)
        else:
            event.status = "failed"

    except requests.RequestException:
        event.status = "failed"

    db.commit()
    db.refresh(event)

    return event