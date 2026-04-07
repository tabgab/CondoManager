"""Building CRUD operations."""
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.building import Building
from app.schemas.building import BuildingCreate, BuildingUpdate


async def get_buildings(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
) -> tuple[list[Building], int]:
    """Get list of buildings with pagination."""
    # Get total count
    count_result = await db.execute(select(func.count()).select_from(Building))
    total = count_result.scalar()

    # Get buildings
    result = await db.execute(
        select(Building).offset(skip).limit(limit)
    )
    buildings = result.scalars().all()

    return list(buildings), total


async def get_building(db: AsyncSession, building_id: str) -> Optional[Building]:
    """Get a building by ID."""
    result = await db.execute(
        select(Building).where(Building.id == building_id)
    )
    return result.scalar_one_or_none()


async def create_building(db: AsyncSession, building_data: BuildingCreate) -> Building:
    """Create a new building."""
    db_building = Building(
        name=building_data.name,
        address=building_data.address,
        city=building_data.city,
        country=building_data.country,
        description=building_data.description,
        manager_id=building_data.manager_id,
    )
    db.add(db_building)
    await db.commit()
    await db.refresh(db_building)
    return db_building


async def update_building(
    db: AsyncSession,
    building: Building,
    update_data: BuildingUpdate,
) -> Building:
    """Update a building."""
    update_dict = update_data.model_dump(exclude_unset=True)

    for field, value in update_dict.items():
        setattr(building, field, value)

    await db.commit()
    await db.refresh(building)
    return building


async def delete_building(db: AsyncSession, building: Building) -> None:
    """Delete a building."""
    await db.delete(building)
    await db.commit()


async def get_building_apartment_count(db: AsyncSession, building_id: str) -> int:
    """Get count of apartments in a building."""
    from app.models.apartment import Apartment
    result = await db.execute(
        select(func.count()).select_from(Apartment).where(Apartment.building_id == building_id)
    )
    return result.scalar()
