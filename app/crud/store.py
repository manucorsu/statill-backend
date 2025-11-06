from ..models.user import User, StoreRoleEnum

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.store import Store
from app.models.sale import Sale
from app.models.products_sales import ProductsSales
from app.models.product import Product
from ..models.verification_code import VerificationCode
from app.schemas.store import StoreCreate

from ..mailing import send_verification_code, send_email

from ..utils import utcnow


def get_all(session: Session):
    """
    Retrieves all stores from the database.
    Args:
        session (Session): The SQLAlchemy session to use for the query.
    Returns:
        list[Store]: A list of all stores.
    """
    return session.query(Store).all()


def get_by_id(id: int, session: Session):
    """
    Retrieves a store by its ID.
    Args:
        id (int): The ID of the store to retrieve.
        session (Session): The SQLAlchemy session to use for the query.
    Returns:
        Store: The store with the specified ID.
    Raises:
        HTTPException(404): If the store with the specified ID does not exist.
    """
    store = session.get(Store, id)
    if store is None:
        raise HTTPException(status_code=404, detail="Store not found")
    return store

ALL_OTCT_NONE = [False for _ in range(7)]
def create(store_data: StoreCreate, session: Session, owner: User):
    """
    Creates a new store in the database.
    Args:
        store_data (StoreCreate): The store data to create.
        session (Session): The SQLAlchemy session to use for the insert.
        owner (User): The user who will own the store.

    Raises:
        HTTPException(400): If the user already owns a store or if the store hours are invalid.
    Returns:
        int: The ID of the newly created store.
    """
    user = owner
    if user.store_id:
        raise HTTPException(
            400,
            f"User must be disassociated from store {user.store_id} before associating them to a new one.",
        )
    if (store_data.opening_times == ALL_OTCT_NONE) or (store_data.closing_times == ALL_OTCT_NONE):
        raise HTTPException("Stores must be open in at least one day of the week")
    for index, ct in enumerate(store_data.closing_times):
        ot = store_data.opening_times[index]

        if (ct is None or ot is None) and ct != ot:
            raise HTTPException(
                400,
                detail="A store's opening time cannot be None if its closing time has a value (and vice-versa)",
            )

        if (ct is not None and ot is not None) and (ct <= ot):
            raise HTTPException(
                400, "A store's closing time must be after its opening time."
            )

    store_dump = store_data.model_dump()
    store = Store(**store_dump)

    session.add(store)
    session.flush()
    session.refresh(store)

    user = owner
    user.store_id = store.id
    user.store_role = StoreRoleEnum.OWNER

    session.commit()
    return store.id


def update(id: int, store_data: StoreCreate, session: Session):
    """
    Updates a store by its ID.
    Args:
        id (int): The ID of the store to update.
        store_data (StoreCreate): The updated store data.
        session (Session): The SQLAlchemy session to use for the update.
    Returns:
        None
    Raises:
        HTTPException(404): If the store with the specified ID does not exist.
    """
    for index, ct in enumerate(store_data.closing_times):
        ot = store_data.opening_times[index]

        if (ct is None or ot is None) and ct != ot:
            raise HTTPException(
                400,
                detail="A store's opening time cannot be None if its closing time has a value (and vice-versa)",
            )

        if (ct is not None and ot is not None) and (ct <= ot):
            raise HTTPException(
                400, "A store's closing time must be after its opening time."
            )

    store = get_by_id(id, session)

    updates = store_data.model_dump(exclude_unset=True)

    for field, value in updates.items():
        setattr(store, field, value)

    session.commit()


def delete(id: int, session: Session):
    """
    Deletes a store by its ID, cascading delete to products, sales, and products_sales, but not users.
    Args:
        id (int): The ID of the store to delete.
        session (Session): The SQLAlchemy session to use for the delete.
    Returns:
        None
    Raises:
        HTTPException(404): If the store with the specified ID does not exist.
    """
    item = get_by_id(id, session)

    # Delete all products associated with this store
    products = session.query(Product).filter(Product.store_id == id).all()
    for product in products:
        session.delete(product)

    # Delete all sales associated with this store
    sales = session.query(Sale).filter(Sale.store_id == id).all()
    for sale in sales:
        products_sales = (
            session.query(ProductsSales).filter(ProductsSales.sale_id == sale.id).all()
        )

        session.delete(sale)
        for ps in products_sales:
            session.delete(ps)

    # Do NOT delete users, just disassociate them
    from .user import get_by_store_id

    users = get_by_store_id(id, session)
    for user in users:
        user.store_id = None
        user.store_role = None

    session.delete(item)
    session.commit()


def add_cashier(cashier_email_address: str, store_owner: User, session: Session):
    if store_owner.store_role != StoreRoleEnum.OWNER:
        raise HTTPException(400, "User has to own a store to add cashiers to it")

    from .user import get_by_email

    cashier_user = get_by_email(cashier_email_address, session, raise_404=True)
    if cashier_user.store_id:
        raise HTTPException(400, "Cashier already belongs to a store")

    cashier_user.store_id = store_owner.store_id
    cashier_user.store_role = StoreRoleEnum.CASHIER_PENDING
    send_verification_code(
        session,
        cashier_user,
        "store_add",
        store=get_by_id(store_owner.store_id, session),
    )


def accept_cashier_add(code: str, session: Session, cashier: User):
    verification = (
        session.query(VerificationCode)
        .filter(
            VerificationCode.code == code
            and VerificationCode.user_id == cashier.id
            and VerificationCode.type == "store_add"
        )
        .first()
    )

    if not verification:
        raise HTTPException(status_code=400, detail="Invalid or expired code")

    if verification.expires_at < utcnow():
        session.delete(verification)
        session.commit()
        raise HTTPException(status_code=400, detail="Code expired")

    cashier.store_role = StoreRoleEnum.CASHIER
    session.commit()


def remove_cashier(cashier_email_address: str, store_owner: User, session: Session):
    if store_owner.store_role != "owner":
        raise HTTPException(400, "User has to own a store to add cashiers to it")

    from .user import get_by_email

    cashier_user = get_by_email(cashier_email_address, session, raise_404=True)

    if (
        cashier_user.store_id != store_owner.store_id
        or cashier_user.store_role not in ("cashier", "cashier-pending")
    ):
        raise HTTPException(400, "The target user must be a cashier at this store")

    cashier_user.store_id = None
    cashier_user.store_role = None

    session.commit()

    store = get_by_id(store_owner.store_id, session)
    send_email(
        cashier_user,
        f"Fuiste eliminado de {store.name}",
        htmlBody=f"""
                 <html>
                    <h1>Fuiste eliminado de {store.name}</h1>
                    <p>Contactate con el dueño de {store.name} para más información.</p>
                 </html>
                 """,
    )
