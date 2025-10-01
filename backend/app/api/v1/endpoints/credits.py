"""Credit management endpoints."""

import uuid
import logging
from typing import List, Dict
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.models.schemas import (
    CreditCreate, CreditUpdate, CreditResponse, SuccessResponse
)
from app.services.finance_service import FinanceService
from app.services.exceptions import ValidationError, CreditNotFoundError

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/", response_model=SuccessResponse)
async def create_credit(
    credit_data: CreditCreate,
    device_id: str = Query(..., description="Device identifier"),
    db: AsyncSession = Depends(get_db_session)
):
    """Create a new credit."""
    try:
        service = FinanceService(db)
        credit_id = await service.create_credit(device_id, credit_data)
        
        # Get the created credit to return in response
        created_credit = await service.get_credit_by_id(credit_id, device_id)
        
        return SuccessResponse(
            message="Credit created successfully",
            data=created_credit
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating credit: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=Dict[str, List[CreditResponse]])
async def get_credits_grouped(
    device_id: str = Query(..., description="Device identifier"),
    db: AsyncSession = Depends(get_db_session)
):
    """Get all credits grouped by category."""
    try:
        service = FinanceService(db)
        credits = await service.get_credits_grouped_by_category(device_id)
        return credits
    except Exception as e:
        logger.error(f"Error fetching grouped credits: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{credit_id}", response_model=CreditResponse)
async def get_credit(
    credit_id: uuid.UUID,
    device_id: str = Query(..., description="Device identifier"),
    db: AsyncSession = Depends(get_db_session)
):
    """Get a specific credit by ID."""
    try:
        service = FinanceService(db)
        credit = await service.get_credit_by_id(credit_id, device_id)
        return credit
    except CreditNotFoundError:
        raise HTTPException(status_code=404, detail="Credit not found")
    except Exception as e:
        logger.error(f"Error fetching credit {credit_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{credit_id}", response_model=SuccessResponse)
async def update_credit(
    credit_id: uuid.UUID,
    credit_data: CreditUpdate,
    device_id: str = Query(..., description="Device identifier"),
    db: AsyncSession = Depends(get_db_session)
):
    """Update an existing credit."""
    try:
        service = FinanceService(db)
        await service.update_credit(credit_id, device_id, credit_data)
        
        # Get the updated credit to return in response
        updated_credit = await service.get_credit_by_id(credit_id, device_id)
        
        return SuccessResponse(
            message="Credit updated successfully",
            data=updated_credit
        )
    except CreditNotFoundError:
        raise HTTPException(status_code=404, detail="Credit not found")
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating credit {credit_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{credit_id}", response_model=SuccessResponse)
async def delete_credit(
    credit_id: uuid.UUID,
    device_id: str = Query(..., description="Device identifier"),
    db: AsyncSession = Depends(get_db_session)
):
    """Delete a credit."""
    try:
        service = FinanceService(db)
        await service.delete_credit(credit_id, device_id)
        
        return SuccessResponse(message="Credit deleted successfully")
    except CreditNotFoundError:
        raise HTTPException(status_code=404, detail="Credit not found")
    except Exception as e:
        logger.error(f"Error deleting credit {credit_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
