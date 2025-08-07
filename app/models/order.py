from app.database.base import Base
from sqlalchemy import Column, Integer, BigInteger, CheckConstraint, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import TIME
from sqlalchemy.orm import relationship
import enum
from .user import User
from .orders_products import OrdersProducts


class StatusEnum(enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    RECIEVED = "recieved"


class Order(Base):
    __tablename__ = "orders"
    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    store_id = Column(BigInteger, ForeignKey("stores.id"), nullable=False)
    created_at = Column(TIME(timezone=True), nullable=False)
    status = Column(Enum(StatusEnum, name="status_enum"), nullable=False)
    received_at = Column(TIME(timezone=True), nullable=True)
    payment_method = Column(Integer, nullable=False)

    # Relationships
    user = relationship("User", back_populates="order")
    store = relationship("Store", back_populates="order")
    orders_products = relationship("OrdersProducts", back_populates="order")

    # Constraints
    __table_args__ = (
        CheckConstraint("payement_method IN (0,1,2,3)", name="payement_method_check"),
    )
