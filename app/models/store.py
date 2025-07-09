from app.database.base import Base
from sqlalchemy import Column, String, BigInteger, Boolean, CheckConstraint
from sqlalchemy.dialects.postgresql import ARRAY, BOOLEAN, TIME
from sqlalchemy.orm import relationship
from .order import Order


class Store(Base):
    __tablename__ = "stores"
    id = Column(BigInteger, primary_key=True)
    name = Column(String(60), nullable=False)
    category = Column(BigInteger, nullable=False)
    address = Column(String, nullable=False)
    preorder_enabled = Column(Boolean, nullable=False)
    ps_enabled = Column(Boolean, nullable=False)
    opening_times = Column(ARRAY(TIME(timezone=True)), nullable=False)
    closing_times = Column(ARRAY(TIME(timezone=True)), nullable=False)
    payment_methods = Column(ARRAY(BOOLEAN), nullable=False)

    # Relationships
    order = relationship("Order", back_populates="store")
    sale = relationship("Sale", back_populates="store")
    review = relationship("Review", back_populates="store")
    points = relationship("Points", back_populates="store")
    product = relationship("Product", back_populates="store")

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "array_length(days_open, 1) = 7", name="days_open_length_check"
        ),
        CheckConstraint(
            "array_length(opening_times, 1) = 7", name="opening_times_length_check"
        ),
        CheckConstraint(
            "array_length(closing_times, 1) = 7", name="closing_times_length_check"
        ),
        CheckConstraint(
            "array_length(payment_methods, 1) = 4", name="payment_methods_length_check"
        ),
    )
