from app.database.base import Base
from sqlalchemy import Column, BigInteger, ForeignKey
from sqlalchemy.dialects.postgresql import DOUBLE_PRECISION
from sqlalchemy.orm import relationship


class ProductsSales(Base):
    __tablename__ = "products_sales"
    id = Column(BigInteger, primary_key=True)
    sale_id = Column(BigInteger, ForeignKey("sales.id"), nullable=False)
    product_id = Column(BigInteger, ForeignKey("products.id"), nullable=False)
    quantity = Column(DOUBLE_PRECISION, nullable=False)

    # Relationships
    sale = relationship("Sale", back_populates="products_sales")
    product = relationship("Product", back_populates="products_sales")
