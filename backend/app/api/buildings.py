"""Building API endpoints with RBAC."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import get_db
from app.models.building import Building
from app.models.user import User
from app.schemas.building import BuildingCreate, BuildingUpdate, BuildingResponse, BuildingListResponse
from app.schemas.apartment import ApartmentCreate, ApartmentUpdate, ApartmentResponse, ApartmentListResponse
from app.crud import building as crud_building
from app.crud import apartment as crud_apartment
from app.dependencies.auth import require_manager, get_current_user

router = APIRouter(prefix="/buildings", tags=["buildings"])


def is_manager_or_admin(role: str) -> bool:
    """Check if role has manager privileges."""
    return role in ("super_admin", "manager")


@router.get("", response_model=BuildingListResponse)
async def list_buildings(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_manager),
):
    """List all buildings (manager only)."""
    buildings, total = await crud_building.get_buildings(db, skip=skip, limit=limit)
    return {
        "items": buildings,
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.get("/{building_id}", response_model=BuildingResponse)
async def get_building(
    building_id: str,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_manager),
):
    """Get a building by ID."""
    building = await crud_building.get_building(db, building_id)
    if not building:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Building not found",
        )
    return building


@router.post("", response_model=BuildingResponse, status_code=status.HTTP_201_CREATED)
async def create_building(
    building_data: BuildingCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_manager),
):
    """Create a new building (manager only)."""
    building = await crud_building.create_building(db, building_data)
    return building


@router.patch("/{building_id}", response_model=BuildingResponse)
async def update_building(
    building_id: str,
    update_data: BuildingUpdate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_manager),
):
    """Update a building (manager only)."""
    building = await crud_building.get_building(db, building_id)
    if not building:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Building not found",
        )
    
    updated_building = await crud_building.update_building(db, building, update_data)
    return updated_building


@router.delete("/{building_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_building(
    building_id: str,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_manager),
):
    """Delete a building (manager only, if no apartments)."""
    building = await crud_building.get_building(db, building_id)
    if not building:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Building not found",
        )
    
    # Check if building has apartments
    apartment_count = await crud_building.get_building_apartment_count(db, building_id)
    if apartment_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete building with existing apartments",
        )
    
    await crud_building.delete_building(db, building)
    return None


@router.get("/{building_id}/apartments", response_model=ApartmentListResponse)
async def list_apartments_by_building(
    building_id: str,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List apartments in a building."""
    # Check building exists
    building = await crud_building.get_building(db, building_id)
    if not building:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Building not found",
        )
    
    # For owners/tenants, filter to show only their apartments
    if not is_manager_or_admin(current_user.role):
        # Get apartments filtered by owner/tenant
        apartments = await crud_apartment.get_apartments_by_owner(db, current_user.id, skip, limit)
        if current_user.role == "tenant":
            apartments = await crud_apartment.get_apartments_by_tenant(db, current_user.id, skip, limit)
        # Filter by building
        apartments = [a for a in apartments if a.building_id == building_id]
        total = len(apartments)
    else:
        apartments, total = await crud_apartment.get_apartments_by_building(
            db, building_id, skip=skip, limit=limit
        )
    
    return {
        "items": apartments,
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.post("/{building_id}/apartments", response_model=ApartmentResponse, status_code=status.HTTP_201_CREATED)
async def create_apartment(
    building_id: str,
    apartment_data: ApartmentCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_manager),
):
    """Create a new apartment in a building (manager only)."""
    from app.crud import user as crud_user
    
    # Check building exists
    building = await crud_building.get_building(db, building_id)
    if not building:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Building not found",
        )
    
    # Validate owner exists if provided
    if apartment_data.owner_id:
        owner = await crud_user.get_user_by_id(db, apartment_data.owner_id)
        if not owner:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Owner user not found",
            )
    
    # Validate tenant exists if provided
    if apartment_data.tenant_id:
        tenant = await crud_user.get_user_by_id(db, apartment_data.tenant_id)
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant user not found",
            )
    apartment = await crud_apartment.create_apartment(db, building_id, apartment_data)
    
    # Reload apartment with owner/tenant relationships
    apartment = await crud_apartment.get_apartment(db, apartment.id)
    return apartment
