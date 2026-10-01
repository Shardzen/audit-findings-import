from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session
from datetime import date, datetime

from app.db import get_db
from app.errors import AppError
from app.models import Finding, User
from app.security import require_role, get_current_user
from pydantic import BaseModel, ConfigDict
from typing import Optional, Literal

router = APIRouter(prefix="/findings", tags=["findings"])

class FindingResponse(BaseModel):
    id : int
    ref : str
    asset : str
    title : str
    severity : str
    detected_on : date 
    status : str
    created_at : datetime
    resolved_at : Optional[datetime] = None
    resolved_by : Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class PaginatedFindings(BaseModel):
    items: list[FindingResponse]
    page: int
    per_page: int
    total: int

@router.get("", response_model=PaginatedFindings)
def list_findings(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    severity: Optional[Literal["faible", "moyenne", "forte"]] = Query(None),
    status: Optional[Literal["ouvert", "corrige"]] = Query(None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    query = db.query(Finding)
    if severity is not None:
        query = query.filter(Finding.severity == severity)
    if status is not None:
        query = query.filter(Finding.status == status)

    total = query.count()
    items = (
        query.order_by(Finding.id.asc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )
    return PaginatedFindings(items=items, page=page, per_page=per_page, total=total)

@router.get("/{finding_id}", response_model=FindingResponse)
def get_finding(
    finding_id: int = Path(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    finding = db.get(Finding, finding_id)
    if finding is None:
        raise AppError(404, "not_found", f"Constat {finding_id} introuvable")
    return finding

