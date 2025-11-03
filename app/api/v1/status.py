from fastapi import APIRouter
from app.schemas.general import APIResponse

from ..generic_tags import public

name = "status"
router = APIRouter()


@router.get("/", response_model=APIResponse, tags=public)
def get_status():
    """
    Checks the status of the API.

    Returns a simple status message indicating that the API is operational.

    Returns:
        APIResponse: A response indicating the API status.
    """
    return APIResponse(
        successful=True,
        data={"status": "ok"},
        message="Successfully performed a status check.",
    )
