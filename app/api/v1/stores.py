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

import app.api.generic_tags as tags

from ...utils import owns_a_store_raise

name = "stores"
router = APIRouter()


@router.get("/", response_model=GetAllStoresResponse, tags=tags.public)
def get_all_stores(db: Session = Depends(get_db)):
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


@router.get("/{id}", response_model=GetStoreResponse, tags=tags.requires_active_user)
def get_store_by_id(
    id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user_require_active),
):
    """
    Retrieves a store by its ID.

    Args:
        id (int): The ID of the store to retrieve.
        db (Session): The SQLAlchemy session to use for the query.
        _ (User): The current authenticated admin user. Unused, is only there to enforce auth and activation.
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
    tags=tags.requires_active_user,
)
def create_store(
    store: StoreCreate,
    db: Session = Depends(get_db),
    owner_user=Depends(get_current_user_require_active),
):
    """
    Creates a store.

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


@router.put("/{id}", response_model=APIResponse, tags=tags.requires_admin)
def update_store_by_id(
    id: int,
    store: StoreUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user_require_admin),
):
    """
    Updates a store by its ID.

    Args:
        id (int): The ID of the store to update.
        store (StoreUpdate): The updated store data.
        db (Session): The SQLAlchemy session to use for the update.
        _ (User): The current authenticated admin user. Unused, is only there to enforce admin auth.

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


@router.put("/my", response_model=APIResponse, tags=tags.requires_active_user)
def update_own_store(
    store: StoreUpdate,
    session: Session = Depends(get_db),
    owner_user: User = Depends(get_current_user_require_active),
):
    """
    Updates the store owned by the current authenticated active user.

    Args:
        store (StoreUpdate): The updated store data.
        session (Session): The SQLAlchemy session to use for the update.
        owner_user (User): The authenticated and active user who owns the store.

    Returns:
        APIResponse: A response indicating the success of the update operation.

    Raises:
        HTTPException(400): If the user does not own a store (raised by crud.update)
    """
    owns_a_store_raise(owner_user)
    crud.update(owner_user.store_id, store, session)
    return APIResponse(
        successful=True, data=None, message="Successfully updated the Store."
    )


@router.delete("/{id}", response_model=APIResponse, tags=tags.requires_admin)
def delete_store_by_id(
    id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user_require_admin),
):
    """
    Deletes a store by its ID.

    Args:
        id (int): The ID of the store to delete.
        db (Session): The SQLAlchemy session to use for the delete.
        _ (User): The current authenticated admin user. Unused, is only there to enforce admin auth.

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


@router.delete("/my", response_model=APIResponse, tags=tags.requires_active_user)
def delete_own_store(
    session: Session = Depends(get_db),
    owner_user: User = Depends(get_current_user_require_active),
):
    """
    Deletes the store owned by the current authenticated active user.

    Args:
        session (Session): The SQLAlchemy session to use for the delete.
        owner_user (User): The authenticated and active user who owns the store.

    Returns:
        APIResponse: A response indicating the success of the delete operation.

    Raises:
        HTTPException(400): If the user does not own a store (raised by crud.delete)
    """
    owns_a_store_raise(owner_user)
    crud.delete(owner_user.store_id, session)
    return APIResponse(
        successful=True,
        data=None,
        message=f"Successfully deleted the Store with id {owner_user.store_id}.",
    )


@router.post("/cashier", response_model=SuccessfulResponse, status_code=202, tags=tags.requires_active_user)
def add_cashier(
    cashier_email_address: AddCashier,
    session: Session = Depends(get_db),
    owner_user: User = Depends(get_current_user_require_active),
):
    owns_a_store_raise(owner_user)
    crud.add_cashier(cashier_email_address.email_address, owner_user, session)
    return SuccessfulResponse(
        data=None,
        message=f"Successfully invited {cashier_email_address} to join the store.",
    )


@router.patch("/cashier/accept", response_model=SuccessfulResponse, tags=tags.requires_active_user)
def accept_cashier_add(
    code: str,
    session: Session = Depends(get_db),
    cashier: User = Depends(get_current_user_require_active),
):
    crud.accept_cashier_add(code, session, cashier)
    return SuccessfulResponse(
        data=None, message="Succesfully accepted the cashier invitation."
    )
