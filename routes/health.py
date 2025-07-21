from fastapi import APIRouter, status

router = APIRouter(
    prefix="/health",
    tags=["health"],
)


@router.get("/", status_code=status.HTTP_200_OK)
async def health_check():
    """
    Health check endpoint for the API.
    Returns 200 OK if the API is running.
    """
    return {"status": "ok", "message": "API is running"} 