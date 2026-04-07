"""Report messages API endpoints for threaded conversations."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import get_db
from app.models.user import User, UserRole
from app.dependencies.auth import get_current_user, require_manager
from app.schemas.report_message import (
    ReportMessageCreate,
    ReportMessageResponse,
    ReportMessageListResponse
)
from app import crud

router = APIRouter()


@router.get("/reports/{report_id}/messages", response_model=ReportMessageListResponse)
async def list_report_messages(
    report_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List messages in a report thread."""
    # First check if report exists and user has access
    report = await crud.report.get_report(db, report_id)

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    # Check access - manager sees all, submitter sees their own
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.MANAGER]:
        if report.submitted_by_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to view this report's messages")

    items, total = await crud.report_message.get_messages_by_report(db, report_id, skip, limit)

    return ReportMessageListResponse(
        items=[ReportMessageResponse.model_validate(item) for item in items],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.post("/reports/{report_id}/messages", response_model=ReportMessageResponse, status_code=status.HTTP_201_CREATED)
async def create_report_message(
    report_id: str,
    message_data: ReportMessageCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Add a message to a report thread."""
    # Check if report exists
    report = await crud.report.get_report(db, report_id)

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    # Check access - managers and report submitter can add messages
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.MANAGER]:
        if report.submitted_by_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to add messages to this report")

    message = await crud.report_message.create_message(db, report_id, message_data, current_user.id)
    return message
