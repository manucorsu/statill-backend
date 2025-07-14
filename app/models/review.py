from app.database.base import Base
from sqlalchemy import Column, String, Integer, BigInteger, CheckConstraint, ForeignKey
from sqlalchemy.orm import relationship


class Review(Base):
    __tablename__ = "reviews"
    id = Column(BigInteger, primary_key=True)
    store_id = Column(BigInteger, ForeignKey("stores.id"), nullable=False)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    stars = Column(Integer, nullable=False)
    desc = Column(String)

    # Relationships
    user = relationship("User", back_populates="review")
    store = relationship("Store", back_populates="review")

    # Constraints
    __table_args__ = (CheckConstraint("stars IN (1,2,3,4,5)", name="stars_check"),)
