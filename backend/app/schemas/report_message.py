"""Report message schemas."""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class ReportMessageCreate(BaseModel):
    content: str


class ReportMessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    report_id: str
    sender_id: Optional[str] = None
    content: str
    created_at: datetime
    updated_at: datetime


class ReportMessageListResponse(BaseModel):
    items: List[ReportMessageResponse]
    total: int
    skip: int = 0
    limit: int = 100
