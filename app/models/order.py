from app.database.base import Base
from sqlalchemy import Column, String, BigInteger, Boolean, CheckConstraint, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY, BOOLEAN, TIME
from sqlalchemy.orm import relationship

class Order(Base):
    __tablename__: "orders"
    id = Column(BigInteger, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    store_id = Column(Integer, ForeignKey('stores.id'), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="orders")
    store = relationship("Store", back_populates="orders")

