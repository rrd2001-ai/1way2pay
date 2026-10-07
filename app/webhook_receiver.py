import hashlib
import hmac
import json

from fastapi import FastAPI, Header, HTTPException, Request

app = FastAPI(title="1Way2Pay Webhook Receiver")

WEBHOOK_SECRET = "whsec_test_7f3a9c2d81e64b5a"


def verify_signature(
    payload: dict,
    signature: str,
    secret: str,
) -> bool:

    payload_bytes = json.dumps(
        payload,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")

    expected_signature = (
        "sha256="
        + hmac.new(
            secret.encode("utf-8"),
            payload_bytes,
            hashlib.sha256,
        ).hexdigest()
    )

    return hmac.compare_digest(
        signature,
        expected_signature,
    )


@app.post("/webhook")
async def receive_webhook(
    request: Request,
    x_1way2pay_signature: str | None = Header(
        default=None,
        alias="X-1Way2Pay-Signature",
    ),
):
    payload = await request.json()

    if not x_1way2pay_signature:
        raise HTTPException(
            status_code=401,
            detail="Missing webhook signature",
        )

    if not verify_signature(
        payload=payload,
        signature=x_1way2pay_signature,
        secret=WEBHOOK_SECRET,
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid webhook signature",
        )

    print("\n=== VERIFIED WEBHOOK RECEIVED ===")
    print(payload)
    print("Signature:", x_1way2pay_signature)

    return {
        "received": True,
        "signature_valid": True,
    }