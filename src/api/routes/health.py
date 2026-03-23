"""Health check endpoints."""
from fastapi import APIRouter, HTTPException
from api.dependencies import check_db_connection

router = APIRouter()

@router.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "service": "artifact-api"
    }

@router.get("/health/db")
async def db_health_check():
    """Database connectivity check."""
    try:
        is_connected = check_db_connection()
        if is_connected:
            return {
                "status": "healthy",
                "database": "connected"
            }
        else:
            raise HTTPException(
                status_code=503,
                detail={
                    "error_type": "DB_UNAVAILABLE",
                    "message": "Database connection failed"
                }
            )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=503,
            detail={
                "error_type": "DB_HEALTH_CHECK_FAILED",
                "message": "Database health check failed"
            }
        )
