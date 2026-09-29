from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Finding, User
from app.security import require_role

router = APIRouter(prefix="/findings", tags=["findings"])

class FindingResponse(BaseModel):
    id : int
    ref : str
    asset : str
    title : str
    severity : str
    detected_on : date 
    status : str
    created_at : date
    resolved_at : date
    resoled_by : date

    model_config = ConfigDict(from_attributes=True)


class PaginatedFindings(BaseModel):
    items: list[FindingResponse]
    page: int
    per_page: int
    total: int