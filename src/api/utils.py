"""
Utility routes for application health checks.
"""
 
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
 
from src.database.db import get_db
 
router = APIRouter(tags=["utils"])
 
 
@router.get("/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_db)):
    """
    Check that the application and database are running correctly.
 
    Executes a simple ``SELECT 1`` query against the database.
    Returns a welcome message on success, or raises an HTTP 500
    error if the database is unreachable or misconfigured.
 
    :param db: Async database session.
    :return: Dict with a welcome message.
    :raises HTTPException: 500 if the database check fails.
    """
    try:
        result = await db.execute(text("SELECT 1"))
        result = result.scalar_one_or_none()
 
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database is not configured correctly",
            )
 
        return {"message": "Welcome to FastAPI!"}
 
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error connecting to the database",
        )