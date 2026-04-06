"""API endpoints for push subscription management."""
import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import get_db
from app.models.user import User
from app.dependencies.auth import get_current_active_user
from app.schemas.push_subscription import (
    PushSubscriptionCreate,
    PushSubscriptionResponse,
    PushSubscriptionListResponse,
    UnsubscribeRequest,
    VapidPublicKeyResponse,
)
from app.services.push_notification import push_service
from app.core.config import get_settings
import app.crud.push_subscription as push_subscription_crud

logger = logging.getLogger(__name__)

router = APIRouter(tags=["push_notifications"])


@router.get("/push-subscriptions/vapid-public-key", response_model=VapidPublicKeyResponse)
async def get_vapid_public_key():
    """Get VAPID public key for browser push subscription."""
    settings = get_settings()
    if not settings.VAPID_PUBLIC_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Web Push not configured - VAPID keys missing",
        )
    return VapidPublicKeyResponse(public_key=settings.VAPID_PUBLIC_KEY)


@router.get("/push-subscriptions", response_model=PushSubscriptionListResponse)
async def list_push_subscriptions(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """List all push subscriptions for the current user."""
    subscriptions = await push_subscription_crud.get_subscriptions_by_user(
        db, str(current_user.id)
    )
    
    items = [
        PushSubscriptionResponse(
            id=sub.id,
            endpoint=sub.endpoint,
            device_info=sub.device_info,
            created_at=sub.created_at,
        )
        for sub in subscriptions
    ]
    
    return PushSubscriptionListResponse(items=items, total=len(items))


@router.post("/push-subscriptions", response_model=PushSubscriptionResponse, status_code=status.HTTP_201_CREATED)
async def create_push_subscription(
    subscription_data: PushSubscriptionCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Create or update a push subscription for the current user."""
    subscription = await push_subscription_crud.create_subscription(
        db, subscription_data, str(current_user.id)
    )
    
    return PushSubscriptionResponse(
        id=subscription.id,
        endpoint=subscription.endpoint,
        device_info=subscription.device_info,
        created_at=subscription.created_at,
    )


@router.delete("/push-subscriptions/{subscription_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_push_subscription(
    subscription_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a push subscription (must be owned by current user)."""
    # Get the subscription
    subscription = await push_subscription_crud.get_subscription_by_id(db, subscription_id)
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Push subscription not found",
        )
    
    # Check ownership
    if str(subscription.user_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete another user's subscription",
        )
    
    await push_subscription_crud.delete_subscription(db, subscription_id)
    return None


@router.post("/push-subscriptions/unsubscribe")
async def unsubscribe_by_endpoint(
    request: UnsubscribeRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Unsubscribe by endpoint URL (useful for service workers)."""
    # Find subscription by endpoint
    subscription = await push_subscription_crud.get_subscription_by_endpoint(
        db, request.endpoint
    )
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Push subscription not found",
        )
    
    # Check ownership
    if str(subscription.user_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot unsubscribe another user's subscription",
        )
    
    await push_subscription_crud.delete_subscription_by_endpoint(db, request.endpoint)
    return {"message": "Successfully unsubscribed"}
