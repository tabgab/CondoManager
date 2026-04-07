"""Apartment CRUD operations."""
from typing import Optional

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.apartment import Apartment
from app.models.apartment_user import ApartmentUser
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
    
    # Get apartments with eager loading for owner/tenant and users association
    result = await db.execute(
        select(Apartment)
        .where(Apartment.building_id == building_id)
        .options(
            selectinload(Apartment.owner),
            selectinload(Apartment.tenant),
            selectinload(Apartment.users).selectinload(ApartmentUser.user),
        )
        .offset(skip)
        .limit(limit)
    )
    apartments = result.scalars().all()
    
    return list(apartments), total


async def get_apartment(db: AsyncSession, apartment_id: str) -> Optional[Apartment]:
    """Get an apartment by ID with owner/tenant and users loaded."""
    result = await db.execute(
        select(Apartment)
        .where(Apartment.id == apartment_id)
        .options(
            selectinload(Apartment.owner),
            selectinload(Apartment.tenant),
            selectinload(Apartment.users).selectinload(ApartmentUser.user),
        )
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
    result = await db.execute(
        select(Apartment)
        .where(Apartment.owner_id == owner_id)
        .options(
            selectinload(Apartment.owner),
            selectinload(Apartment.tenant),
            selectinload(Apartment.users).selectinload(ApartmentUser.user),
        )
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
    result = await db.execute(
        select(Apartment)
        .where(Apartment.tenant_id == tenant_id)
        .options(
            selectinload(Apartment.owner),
            selectinload(Apartment.tenant),
            selectinload(Apartment.users).selectinload(ApartmentUser.user),
        )
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())


# --- Apartment-User association CRUD ---

async def add_user_to_apartment(
    db: AsyncSession,
    apartment_id: str,
    user_id: str,
    role: str,
) -> ApartmentUser:
    """Assign a user to an apartment with the given role."""
    apartment_user = ApartmentUser(
        apartment_id=apartment_id,
        user_id=user_id,
        role=role,
    )
    db.add(apartment_user)
    await db.commit()
    await db.refresh(apartment_user)
    return apartment_user


async def remove_user_from_apartment(
    db: AsyncSession,
    apartment_id: str,
    user_id: str,
    role: str,
) -> bool:
    """Remove a user-apartment association. Returns True if deleted, False if not found."""
    result = await db.execute(
        select(ApartmentUser).where(
            and_(
                ApartmentUser.apartment_id == apartment_id,
                ApartmentUser.user_id == user_id,
                ApartmentUser.role == role,
            )
        )
    )
    apartment_user = result.scalar_one_or_none()
    if apartment_user:
        await db.delete(apartment_user)
        await db.commit()
        return True
    return False


async def get_apartment_users(
    db: AsyncSession,
    apartment_id: str,
) -> list[ApartmentUser]:
    """Get all user associations for an apartment."""
    result = await db.execute(
        select(ApartmentUser)
        .where(ApartmentUser.apartment_id == apartment_id)
        .options(selectinload(ApartmentUser.user))
    )
    return list(result.scalars().all())
