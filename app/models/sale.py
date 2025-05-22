from app.database.base import Base
from sqlalchemy import Column, Integer, BigInteger, CheckConstraint, ForeignKey
from sqlalchemy.dialects.postgresql import TIME
from sqlalchemy.orm import relationship

class Sale(Base):
    __tablename__ = "sales"
    id = Column(BigInteger, primary_key=True)
    store_id = Column(BigInteger, ForeignKey('stores.id'), nullable=False)
    user_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
    payement_method  = Column(Integer, nullable=False)
    timestamp = Column(TIME(timezone=True), nullable=False)

    # Relationships
    user = relationship("User", back_populates="order")
    store = relationship("Store", back_populates="order")
    products_sales = relationship("Products_Sales", back_populates="order")

    #Constraints
    __table_args__ = (
        CheckConstraint(
            "payement_method IN (1,2,3,4,5)", name = "payement_method_check"
        ),
    )