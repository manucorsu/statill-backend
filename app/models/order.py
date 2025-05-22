from app.database.base import Base
from sqlalchemy import Column, String, BigInteger, Boolean, CheckConstraint, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import ARRAY, BOOLEAN, TIME
from sqlalchemy.orm import relationship
import enum

class StatusEnum(enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    RECIEVED = "recieved"

class Order(Base):
    __tablename__: "orders"
    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
    store_id = Column(BigInteger, ForeignKey('stores.id'), nullable=False)
    created_at = Column(TIME(timezone=True), nullable=False)
    status = Column(Enum(StatusEnum, name="status_enum"), nullable=False)
    recieved_at = Column(TIME(timezone=True), nullable=False)
    payement_method = Column()
    
    # Relationships
    user = relationship("User", back_populates="orders")
    store = relationship("Store", back_populates="orders")

