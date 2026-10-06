from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from .database import get_db
from .models import Merchant


def get_current_merchant(
    x_api_key: str = Header(...),
    db: Session = Depends(get_db),
):
    merchant = (
        db.query(Merchant)
        .filter(Merchant.api_key == x_api_key)
        .first()
    )

    if not merchant:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key",
        )

    return merchant