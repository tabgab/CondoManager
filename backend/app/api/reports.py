"""Report API endpoints."""
from typing import Optional, Literal
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import get_db
from app.models.user import User, UserRole
from app.dependencies.auth import get_current_user, require_manager
from app.schemas.report import ReportCreate, ReportUpdate, ReportResponse, ReportListResponse, ReportReject
from app import crud

router = APIRouter()


async def get_current_owner_or_tenant(
    current_user: User = Depends(get_current_user)
) -> User:
    """Require owner or tenant role to submit reports."""
    if current_user.role not in [UserRole.OWNER, UserRole.TENANT]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only apartment owners and tenants can submit reports"
        )
    return current_user


@router.get("", response_model=ReportListResponse)
async def list_reports(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[Literal["pending", "acknowledged", "task_created", "rejected", "resolved", "deleted"]] = Query(None),
    priority: Optional[Literal["low", "medium", "high", "urgent"]] = Query(None),
    category: Optional[Literal["maintenance", "cleaning", "safety", "noise", "other"]] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List reports - manager sees all, owner/tenant sees only their own."""
    # Manager can see all reports
    if current_user.role in [UserRole.SUPER_ADMIN, UserRole.MANAGER]:
        reporter_id = None
    else:
        # Owner/tenant only see their own reports
        reporter_id = current_user.id
    
    items, total = await crud.report.get_reports(
        db,
        skip=skip,
        limit=limit,
        status=status,
        priority=priority,
        category=category,
        reporter_id=reporter_id,
    )
    
    return ReportListResponse(
        items=[ReportResponse.model_validate(item) for item in items],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.post("", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def create_report(
    report_data: ReportCreate,
    current_user: User = Depends(get_current_owner_or_tenant),
    db: AsyncSession = Depends(get_db),
):
    """Submit a new report (owner or tenant only)."""
    report = await crud.report.create_report(db, report_data, current_user.id)
    return report


@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a single report by ID."""
    report = await crud.report.get_report(db, report_id)
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Check access permissions
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.MANAGER]:
        if report.reporter_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to view this report")
    
    return report


@router.patch("/{report_id}/acknowledge", response_model=ReportResponse)
async def acknowledge_report(
    report_id: str,
    current_user: User = Depends(require_manager),
    db: AsyncSession = Depends(get_db),
):
    """Manager acknowledges a report."""
    report = await crud.report.get_report(db, report_id)
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    report = await crud.report.acknowledge_report(db, report, current_user.id)
    return report


@router.patch("/{report_id}/reject", response_model=ReportResponse)
async def reject_report(
    report_id: str,
    reject_data: ReportReject,
    current_user: User = Depends(require_manager),
    db: AsyncSession = Depends(get_db),
):
    """Manager rejects a report with reason."""
    report = await crud.report.get_report(db, report_id)
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    report = await crud.report.reject_report(db, report, current_user.id, reject_data.reason)
    return report


@router.patch("/{report_id}/resolve", response_model=ReportResponse)
async def resolve_report(
    report_id: str,
    current_user: User = Depends(require_manager),
    db: AsyncSession = Depends(get_db),
):
    """Manager marks report as resolved."""
    report = await crud.report.get_report(db, report_id)
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    report = await crud.report.resolve_report(db, report)
    return report


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_report(
    report_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete report - owner can delete own, manager can delete any."""
    report = await crud.report.get_report(db, report_id)
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Check permissions
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.MANAGER]:
        if report.reporter_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this report")
    
    await crud.report.delete_report(db, report)
    return None
