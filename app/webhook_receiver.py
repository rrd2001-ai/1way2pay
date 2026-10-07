from fastapi import FastAPI, Request

app = FastAPI(title="1Way2Pay Webhook Receiver")


@app.post("/webhook")
async def receive_webhook(request: Request):
    payload = await request.json()

    print("\n=== WEBHOOK RECEIVED ===")
    print(payload)

    return {
        "received": True
    }