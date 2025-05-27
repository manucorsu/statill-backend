from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def get_status():
    """
    Returns `{"status": "ok"}` with status code 200 (OK).

    Args:
        None
    
    Returns:
        dict: `{"status": "ok"}` (code 200)
    """
    return {"status": "ok"}
