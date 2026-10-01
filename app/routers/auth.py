from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db import get_db
from app.security import authenticate, create_access_token

router = APIRouter(tags=["auth"])


@router.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate(db, form_data.username, form_data.password)
    if user is None:
        raise HTTPException(status_code=401, detail="Identifiants invalides")
    token = create_access_token(user)
    return {"access_token": token, "token_type": "bearer"}