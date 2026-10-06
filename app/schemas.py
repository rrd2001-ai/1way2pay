from pydantic import BaseModel, Field


class PaymentCreate(BaseModel):
    amount: int = Field(gt=0)
    currency: str = "INR"
    order_id: str


class PaymentResponse(BaseModel):
    id: str
    amount: int
    currency: str
    order_id: str
    status: str
    checkout_url: str

    class Config:
        from_attributes = True