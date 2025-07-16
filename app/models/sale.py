from app.database.base import Base
from sqlalchemy import Column, Integer, BigInteger, CheckConstraint, ForeignKey, String
from datetime import datetime, timezone
from sqlalchemy.orm import relationship
from .products_sales import ProductsSales


class Sale(Base):
    __tablename__ = "sales"

    id = Column(BigInteger, primary_key=True)
    store_id = Column(BigInteger, ForeignKey("stores.id"), nullable=False)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=True)
    payment_method = Column(Integer, nullable=False)
    timestamp = Column(
        String(32),
        default=lambda: datetime.now(timezone.utc).isoformat(),
        nullable=False,
    )
    # Relationships
    user = relationship("User", back_populates="sale")
    store = relationship("Store", back_populates="sale")
    products_sales = relationship("ProductsSales", back_populates="sale")

    # Constraints
    __table_args__ = (
        CheckConstraint("payment_method IN (0, 1, 2, 3)", name="payment_method_check"),
    )
