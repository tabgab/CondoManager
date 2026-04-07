"""Apartment CRUD operations."""
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.apartment import Apartment
from app.schemas.apartment import ApartmentCreate, ApartmentUpdate


async def get_apartments_by_building(
    db: AsyncSession,
    building_id: str,
    skip: int = 0,
    limit: int = 100,
) -> tuple[list[Apartment], int]:
    """Get apartments in a building with pagination."""
    # Get total count
    count_result = await db.execute(
        select(func.count()).select_from(Apartment).where(Apartment.building_id == building_id)
    )
    total = count_result.scalar()
    
    # Get apartments with eager loading for owner/tenant
    from sqlalchemy.orm import selectinload
    result = await db.execute(
        select(Apartment)
        .where(Apartment.building_id == building_id)
        .options(selectinload(Apartment.owner), selectinload(Apartment.tenant))
        .offset(skip)
        .limit(limit)
    )
    apartments = result.scalars().all()
    
    return list(apartments), total


async def get_apartment(db: AsyncSession, apartment_id: str) -> Optional[Apartment]:
    """Get an apartment by ID with owner/tenant loaded."""
    from sqlalchemy.orm import selectinload
    result = await db.execute(
        select(Apartment)
        .where(Apartment.id == apartment_id)
        .options(selectinload(Apartment.owner), selectinload(Apartment.tenant))
    )
    return result.scalar_one_or_none()


async def create_apartment(
    db: AsyncSession,
    building_id: str,
    apartment_data: ApartmentCreate,
) -> Apartment:
    """Create a new apartment in a building."""
    db_apartment = Apartment(
        building_id=building_id,
        unit_number=apartment_data.unit_number,
        floor=apartment_data.floor,
        owner_id=apartment_data.owner_id,
        tenant_id=apartment_data.tenant_id,
        description=apartment_data.description,
    )
    db.add(db_apartment)
    await db.commit()
    await db.refresh(db_apartment)
    return db_apartment


async def update_apartment(
    db: AsyncSession,
    apartment: Apartment,
    update_data: ApartmentUpdate,
) -> Apartment:
    """Update an apartment."""
    update_dict = update_data.model_dump(exclude_unset=True)
    
    for field, value in update_dict.items():
        setattr(apartment, field, value)
    
    await db.commit()
    await db.refresh(apartment)
    return apartment


async def delete_apartment(db: AsyncSession, apartment: Apartment) -> None:
    """Delete an apartment."""
    await db.delete(apartment)
    await db.commit()


async def get_apartments_by_owner(
    db: AsyncSession,
    owner_id: str,
    skip: int = 0,
    limit: int = 100,
) -> list[Apartment]:
    """Get apartments owned by a user."""
    from sqlalchemy.orm import selectinload
    result = await db.execute(
        select(Apartment)
        .where(Apartment.owner_id == owner_id)
        .options(selectinload(Apartment.owner), selectinload(Apartment.tenant))
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_apartments_by_tenant(
    db: AsyncSession,
    tenant_id: str,
    skip: int = 0,
    limit: int = 100,
) -> list[Apartment]:
    """Get apartments rented by a tenant."""
    from sqlalchemy.orm import selectinload
    result = await db.execute(
        select(Apartment)
        .where(Apartment.tenant_id == tenant_id)
        .options(selectinload(Apartment.owner), selectinload(Apartment.tenant))
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())
