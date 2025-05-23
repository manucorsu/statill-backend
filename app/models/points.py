from app.database.base import Base
from sqlalchemy import Column, Integer, BigInteger, CheckConstraint, ForeignKey
from sqlalchemy.orm import relationship

class Points(Base):
    __tablename__ = "points"
    id = Column(BigInteger, primary_key=True)
    store_id = Column(BigInteger, ForeignKey('stores.id'), nullable=False)
    user_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
    max = Column(Integer, nullable=False)
    amount = Column(Integer, nullable=False)

    # Relationships
    user = relationship("User", back_populates="points")
    store = relationship("Store", back_populates="points")

    #Constraints
    __table_args__ = (
        CheckConstraint(
            "amount >= 0 AND amount <= max", name = "amount_check"
        ),
    )