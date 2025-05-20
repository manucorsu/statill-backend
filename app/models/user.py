from app.database.base import Base
from sqlalchemy import Column, String, BigInteger, Date, Enum, Boolean
import enum


class GenderEnum(enum.Enum):
    MALE = "M"
    FEMALE = "F"
    OTHER = "X"


class StoreRoleEnum(enum.Enum):
    CASHIER = "cashier"
    OWNER = "owner"


class User(Base):
    __tablename__ = "users"
    id = Column(BigInteger, primary_key=True)
    first_names = Column(String(40), nullable=False)
    last_name = Column(String(40), nullable=False)
    email = Column(String(255), nullable=False)
    password = Column(String, nullable=False)
    birthdate = Column(Date, nullable=False)
    gender = Column(Enum(GenderEnum, name="gender_enum"), nullable=False)
    res_area = Column(String(50), nullable=False)
    is_admin = Column(Boolean, nullable=False)
    store_id = Column(BigInteger)
    store_role = Column(Enum(StoreRoleEnum, name="store_role_enum"), nullable=False)

    #Relationships
    orders = relationship("Order", back_populates="user")

