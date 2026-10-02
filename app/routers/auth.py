from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db import get_db
from app.security import authenticate, create_access_token, unauthorized_error

router = APIRouter(tags=["auth"])


@router.post("/token")
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate(db, form.username, form.password)
    if user is None:
        raise unauthorized_error("Identifiants invalides")
    return {"access_token": create_access_token(user), "token_type": "bearer"}
