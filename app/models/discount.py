from app.database.base import Base
from sqlalchemy import (
    Column,
    Integer,
    BigInteger,
    Date,
    CheckConstraint,
    ForeignKey,
)
from sqlalchemy.dialects.postgresql import ARRAY, BOOLEAN
from sqlalchemy.orm import relationship

INTEGER_MAX_VALUE = 2147483647


class Discount(Base):
    __tablename__ = "discounts"
    id = Column(BigInteger, primary_key=True)
    product_id = Column(BigInteger, ForeignKey("products.id"), nullable=False)
    type = Column(Integer, nullable=False)
    pct_off = Column(Integer, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    days_usable = Column(ARRAY(BOOLEAN), nullable=False)
    min_amount = Column(Integer, nullable=False, default=1)
    max_amount = Column(Integer, nullable=False, default=INTEGER_MAX_VALUE)

    # Relationships
    product = relationship("Product", back_populates="discount")

    # Constraints
    __table_args__ = (
        CheckConstraint("pct_off > 0 AND pct_off <= 100", name="pct_off_check"),
        CheckConstraint("array_length(days_usable, 1) = 7", name="days_usable_check"),
    )
