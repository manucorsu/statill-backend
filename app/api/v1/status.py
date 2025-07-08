from fastapi import APIRouter
from app.schemas.general import APIResponse

router = APIRouter()


@router.get("/", response_model=APIResponse)
def get_status():
    """
    Checks the status of the API.

    Returns a simple status message indicating that the API is operational.
    
    Returns:
        APIResponse: A response indicating the API status.
    """
    return APIResponse(successful=True, data={"status": "ok"}, message="Successfully performed a status check.")
