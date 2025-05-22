from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def get_status():
    """
    Returns `{"status": "ok"}` with status code 200 (OK).
    """
    return {"status": "ok"}
