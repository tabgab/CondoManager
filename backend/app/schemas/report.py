"""Report schemas."""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class ReportBase(BaseModel):
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[str] = None
    apartment_id: Optional[str] = None
    building_id: Optional[str] = None
    photo_url: Optional[str] = None


class ReportCreate(ReportBase):
    pass


class ReportUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[str] = None
    photo_url: Optional[str] = None
    status: Optional[str] = None


class ReportReject(BaseModel):
    reason: str


class ReportResponse(ReportBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    submitted_by_id: Optional[str] = None
    status: str = "pending"
    rejection_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class ReportListResponse(BaseModel):
    items: List[ReportResponse]
    total: int
    skip: int = 0
    limit: int = 100
