from app.database.base import Base
from sqlalchemy import Column, String, Integer, BigInteger, Numeric, ForeignKey
from sqlalchemy.orm import relationship

class Product(Base):
    __tablename__ = "products"
    id = Column(BigInteger, primary_key=True)
    store_id = Column(BigInteger, ForeignKey('stores.id'), nullable=False)
    name = Column(String(100), nullable=False)
    brand = Column(String(30), nullable=False)
    price = Column(Numeric(10,2), nullable=False)
    type = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)
    desc = Column(String, nullable=False)


# Relationships
    store = relationship("Store", back_populates="product")