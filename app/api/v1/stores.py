from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from app.dependencies.db import get_db

from app.schemas.store import (
    StoreCreate,
    GetAllStoresResponse,
    GetStoreResponse,
    StoreUpdate,
    AddCashier,
)
from app.schemas.general import APIResponse, SuccessfulResponse

from app.crud import store as crud

from .auth import get_current_user_require_active, get_current_user_require_admin
from ...models.user import User

import app.api.generic_tags as generic_tags

name = "stores"
router = APIRouter()


@router.get("/", response_model=GetAllStoresResponse, tags=[generic_tags.PUBLIC])
def get_stores(db: Session = Depends(get_db)):
    """
    Retrieves all stores from the database.

    Args:
        db (Session): The SQLAlchemy session to use for the query.

    Returns:
        GetAllStoresResponse: A response containing a list of all stores.
    """
    result = crud.get_all(db)
    return GetAllStoresResponse(
        successful=True, data=result, message="Successfully retrieved all stores."
    )


@router.get("/{id}", response_model=GetStoreResponse, tags=[generic_tags.PUBLIC])
def get_store_by_id(id: int, db: Session = Depends(get_db)):
    """
    Retrieves a store by its ID.

    Args:
        id (int): The ID of the store to retrieve.
        db (Session): The SQLAlchemy session to use for the query.

    Returns:
        GetStoreResponse: A response containing the store with the specified ID.

    Raises:
        HTTPException(400): If the provided ID is invalid (less than or equal to 0).
        HTTPException(404): If the store with the specified ID does not exist.
    """
    result = crud.get_by_id(id, db)
    return GetStoreResponse(
        successful=True,
        data=result,
        message=f"Successfully retrieved the Store with id {result.id}.",
    )


@router.post(
    "/",
    response_model=APIResponse,
    status_code=201,
    tags=[generic_tags.REQUIRES_AUTH, generic_tags.REQUIRES_ACTIVE_USER],
)
def create_store(
    store: StoreCreate,
    db: Session = Depends(get_db),
    owner_user=Depends(get_current_user_require_active),
):
    """
    Creates a store.

    (Requires auth, requires active user)

    Args:
        store (StoreCreate): The store data.
        db (Session): The SQLAlchemy session to use for the query.
        owner_user (User): The authenticated and active user creating the store.
    Raises:
        HTTPException(400): If the user already owns a store or if the store hours are invalid (raised by crud.create)
    """
    store_id = crud.create(store, db, owner=owner_user)
    return APIResponse(
        successful=True,
        data={"id": store_id},
        message=f"Successfully created the Store, which received id {store_id}.",
    )


@router.put("/{id}", response_model=APIResponse)
def update_store(
    id: int,
    store: StoreUpdate,
    db: Session = Depends(get_db),
    owner_user: User = Depends(get_current_user_require_admin),
):
    """
    # IMPORTANTE:
    Este endpoint ahora es exclusivo para admins (por requerir store id), por favor usen **`update_my_store`**!
    #
    Updates a store by its ID.

    (Requires auth, requires active user, requires admin)

    Args:
        id (int): The ID of the store to update.
        store (StoreUpdate): The updated store data.
        db (Session): The SQLAlchemy session to use for the update.

    Returns:
        APIResponse: A response indicating the success of the update operation.

    Raises:
        HTTPException(400): If the provided ID is invalid (less than or equal to 0).
        HTTPException(404): If the store with the specified ID does not exist.
    """
    crud.update(id, store, db)
    return APIResponse(
        successful=True, data=None, message="Successfully updated the Store."
    )


@router.delete("/{id}", response_model=APIResponse)
def delete_store(
    id: int,
    db: Session = Depends(get_db),
    owner_user: User = Depends(get_current_user_require_active),
):
    """
    Deletes a store by its ID.

    (Will require auth in the future)

    Args:
        id (int): The ID of the store to delete.
        db (Session): The SQLAlchemy session to use for the delete.

    Returns:
        APIResponse: A response indicating the success of the delete operation.

    Raises:
        HTTPException(400): If the provided ID is invalid (less than or equal to 0).
        HTTPException(404): If the store  with the specified ID does not exist.
    """
    crud.delete(id, db)
    return APIResponse(
        successful=True,
        data=None,
        message=f"Successfully deleted the Store with id {id}.",
    )


@router.post("/cashier", response_model=SuccessfulResponse, status_code=202)
def add_cashier(
    cashier_email_address: AddCashier,
    session: Session = Depends(get_db),
    owner_user: User = Depends(get_current_user_require_active),
):
    crud.add_cashier(cashier_email_address.email_address, owner_user, session)
    return SuccessfulResponse(
        data=None,
        message=f"Successfully invited {cashier_email_address} to join the store.",
    )


@router.patch("/cashier/accept", response_model=SuccessfulResponse)
def accept_cashier_add(
    code: str,
    session: Session = Depends(get_db),
    cashier: User = Depends(get_current_user_require_active),
):
    crud.accept_cashier_add(code, session, cashier)
    return SuccessfulResponse(
        data=None, message="Succesfully accepted the cashier invitation."
    )
