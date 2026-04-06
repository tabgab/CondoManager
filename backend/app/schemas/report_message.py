"""Report message schemas."""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class ReportMessageCreate(BaseModel):
    content: str
    photo_urls: Optional[List[str]] = None
    is_internal: bool = False


class ReportMessageResponse(ReportMessageCreate):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    report_id: str
    author_id: str
    created_at: datetime


class ReportMessageListResponse(BaseModel):
    items: List[ReportMessageResponse]
    total: int
    skip: int = 0
    limit: int = 100
