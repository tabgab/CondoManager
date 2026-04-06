"""CRUD operations for push subscriptions."""
from typing import Optional, List
from uuid import uuid4
from datetime import datetime

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.push_subscription import PushSubscription
from app.schemas.push_subscription import PushSubscriptionCreate


async def get_subscription_by_id(db: AsyncSession, subscription_id: str) -> Optional[PushSubscription]:
    """Get push subscription by ID."""
    result = await db.execute(
        select(PushSubscription).where(PushSubscription.id == subscription_id)
    )
    return result.scalar_one_or_none()


async def get_subscription_by_endpoint(db: AsyncSession, endpoint: str) -> Optional[PushSubscription]:
    """Get push subscription by endpoint URL."""
    result = await db.execute(
        select(PushSubscription).where(PushSubscription.endpoint == endpoint)
    )
    return result.scalar_one_or_none()


async def get_subscriptions_by_user(db: AsyncSession, user_id: str) -> List[PushSubscription]:
    """Get all push subscriptions for a user."""
    result = await db.execute(
        select(PushSubscription)
        .where(PushSubscription.user_id == user_id)
        .order_by(PushSubscription.created_at.desc())
    )
    return result.scalars().all()


async def create_subscription(
    db: AsyncSession,
    subscription_data: PushSubscriptionCreate,
    user_id: str,
) -> PushSubscription:
    """
    Create or update push subscription.
    
    If a subscription with the same endpoint exists, update it instead of creating new.
    """
    # Check if subscription already exists for this endpoint
    existing = await get_subscription_by_endpoint(db, subscription_data.endpoint)
    
    if existing:
        # Update existing subscription
        existing.p256dh = subscription_data.p256dh
        existing.auth = subscription_data.auth
        existing.device_info = subscription_data.device_info
        existing.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(existing)
        return existing
    
    # Create new subscription
    db_subscription = PushSubscription(
        id=str(uuid4()),
        user_id=user_id,
        endpoint=subscription_data.endpoint,
        p256dh=subscription_data.p256dh,
        auth=subscription_data.auth,
        device_info=subscription_data.device_info,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(db_subscription)
    await db.commit()
    await db.refresh(db_subscription)
    return db_subscription


async def delete_subscription(db: AsyncSession, subscription_id: str) -> bool:
    """Delete push subscription by ID."""
    result = await db.execute(
        delete(PushSubscription).where(PushSubscription.id == subscription_id)
    )
    await db.commit()
    return result.rowcount > 0


async def delete_subscription_by_endpoint(db: AsyncSession, endpoint: str) -> bool:
    """Delete push subscription by endpoint URL."""
    result = await db.execute(
        delete(PushSubscription).where(PushSubscription.endpoint == endpoint)
    )
    await db.commit()
    return result.rowcount > 0


async def delete_subscriptions_by_user(db: AsyncSession, user_id: str) -> int:
    """Delete all push subscriptions for a user. Returns count deleted."""
    result = await db.execute(
        delete(PushSubscription).where(PushSubscription.user_id == user_id)
    )
    await db.commit()
    return result.rowcount
