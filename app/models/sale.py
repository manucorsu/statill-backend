from app.database.base import Base
from sqlalchemy import (
    Column,
    Integer,
    BigInteger,
    CheckConstraint,
    ForeignKey,
    DateTime,
)
from datetime import datetime, timezone
from sqlalchemy.orm import relationship
from .products_sales import ProductsSales


class Sale(Base):
    __tablename__ = "sales"
    
    id = Column(BigInteger, primary_key=True)
    store_id = Column(BigInteger, ForeignKey("stores.id"), nullable=False)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    payment_method = Column(Integer, nullable=False)
    timestamp = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    user = relationship("User", back_populates="sale")
    store = relationship("Store", back_populates="sale")
    products_sales = relationship("ProductsSales", back_populates="sale")

    # Constraints
    __table_args__ = (
        CheckConstraint("payment_method IN (1,2,3,4,5)", name="payment_method_check"),
    )
