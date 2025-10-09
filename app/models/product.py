from app.database.base import Base
from sqlalchemy import Column, String, Integer, BigInteger, Numeric, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import DOUBLE_PRECISION
from sqlalchemy.orm import relationship
from app.models.store import Store
from .products_sales import ProductsSales
from .discount import Discount


class Product(Base):
    __tablename__ = "products"
    id = Column(BigInteger, primary_key=True)
    store_id = Column(BigInteger, ForeignKey("stores.id"), nullable=False)
    name = Column(String(100), nullable=False)
    brand = Column(String(30), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    points_price = Column(Integer, nullable=True)
    type = Column(Integer, nullable=False)
    quantity = Column(DOUBLE_PRECISION, nullable=False)
    desc = Column(String, nullable=False)
    hidden = Column(Boolean, nullable=False)
    barcode = Column(String)

    # Relationships
    store = relationship("Store", back_populates="product")
    products_sales = relationship("ProductsSales", back_populates="product")
    discount = relationship("Discount", back_populates="product")
    orders_products = relationship("OrdersProducts", back_populates="product")
