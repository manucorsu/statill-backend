from app.database.base import Base
from sqlalchemy import Column, Integer, BigInteger, ForeignKey
from sqlalchemy.orm import relationship

class OrdersProducts(Base):
    __tablename__ = "orders_products"
    id = Column(BigInteger, primary_key=True)
    order_id = Column(BigInteger, ForeignKey('orders.id'), nullable=False)
    product_id = Column(BigInteger, ForeignKey('products.id'), nullable=False)
    quantity = Column(Integer, nullable=False)

    # Relationships
    order = relationship("Order", back_populates="orders_products")
    product = relationship("Product", back_populates="orders_products")