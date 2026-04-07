"""Apartment API endpoints with RBAC."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import get_db
from app.models.apartment import Apartment
from app.models.user import User
from app.schemas.apartment import ApartmentCreate, ApartmentUpdate, ApartmentResponse, ApartmentListResponse
from app.crud import apartment as crud_apartment
from app.crud import user as crud_user
from app.dependencies.auth import require_manager, get_current_user

router = APIRouter(prefix="/apartments", tags=["apartments"])


def is_manager_or_admin(role: str) -> bool:
    """Check if role has manager privileges."""
    return role in ("super_admin", "manager")


async def check_apartment_access(
    apartment: Apartment,
    current_user: User,
) -> bool:
    """Check if user has access to view this apartment."""
    # Managers/admins have access to all apartments
    if is_manager_or_admin(current_user.role):
        return True
    # Owners can view their own apartments  
    if current_user.role == "owner" and apartment.owner_id == current_user.id:
        return True
    # Tenants can view their rented apartments
    if current_user.role == "tenant" and apartment.tenant_id == current_user.id:
        return True
    return False


async def check_apartment_modify_access(
    apartment: Apartment,
    current_user: User,
) -> bool:
    """Check if user can modify this apartment."""
    # Managers/admins have full modify access
    if is_manager_or_admin(current_user.role):
        return True
    # Owners can update their own apartment details
    if current_user.role == "owner" and apartment.owner_id == current_user.id:
        return True
    return False


@router.get("/{apartment_id}", response_model=ApartmentResponse)

@router.get("", response_model=ApartmentListResponse)
async def list_apartments(
    building_id: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List apartments, optionally filtered by building_id."""
    if not building_id:
        return ApartmentListResponse(items=[], total=0, skip=0, limit=100)
    apartments, total = await crud_apartment.get_apartments_by_building(db, building_id)
    return ApartmentListResponse(items=apartments, total=total, skip=0, limit=100)


@router.post("", response_model=ApartmentResponse, status_code=201)
async def create_apartment(
    data: ApartmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_manager),
):
    """Create a new apartment in a building. Requires manager role."""
    apartment = await crud_apartment.create_apartment(db, data.building_id, data)
    return apartment

async def get_apartment(
    apartment_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get an apartment by ID."""
    apartment = await crud_apartment.get_apartment(db, apartment_id)
    if not apartment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Apartment not found",
        )
    
    # Check access
    if not await check_apartment_access(apartment, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this apartment",
        )
    
    return apartment


@router.patch("/{apartment_id}", response_model=ApartmentResponse)
async def update_apartment(
    apartment_id: str,
    update_data: ApartmentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an apartment."""
    apartment = await crud_apartment.get_apartment(db, apartment_id)
    if not apartment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Apartment not found",
        )
    
    # Check modify access
    if not await check_apartment_modify_access(apartment, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this apartment",
        )
    
    # Owners can only update certain fields (not owner_id, tenant_id)
    if not is_manager_or_admin(current_user.role):
        # Remove restricted fields from update
        update_dict = update_data.model_dump(exclude_unset=True)
        update_dict.pop("owner_id", None)
        update_dict.pop("tenant_id", None)
        update_data = ApartmentUpdate(**update_dict)
    
    # Validate owner/tenant exist if being updated
    if update_data.owner_id:
        owner = await crud_user.get_user_by_id(db, update_data.owner_id)
        if not owner:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Owner user not found",
            )
    
    if update_data.tenant_id:
        tenant = await crud_user.get_user_by_id(db, update_data.tenant_id)
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant user not found",
            )
    
    updated_apartment = await crud_apartment.update_apartment(db, apartment, update_data)
    return updated_apartment


@router.delete("/{apartment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_apartment(
    apartment_id: str,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_manager),
):
    """Delete an apartment (manager only)."""
    apartment = await crud_apartment.get_apartment(db, apartment_id)
    if not apartment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Apartment not found",
        )
    
    await crud_apartment.delete_apartment(db, apartment)
    return None
