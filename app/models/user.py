from app.database.base import Base
from sqlalchemy import Column, String, BigInteger, Date, Enum, Boolean
import enum
from sqlalchemy.orm import relationship
from .sale import Sale
from .review import Review
from .points import Points
from .verification_code import VerificationCode


class GenderEnum(str, enum.Enum):
    MALE = "M"
    FEMALE = "F"
    OTHER = "X"


class StoreRoleEnum(str, enum.Enum):
    CASHIER = "cashier"
    CASHIER_PENDING = (
        "cashier_pending"  # A store owner added them but they haven't accepted yet
    )
    OWNER = "owner"


class User(Base):
    __tablename__ = "users"
    id = Column(BigInteger, primary_key=True)
    first_names = Column(String(40), nullable=False)
    last_name = Column(String(40), nullable=False)
    email = Column(String(255), nullable=False)
    password = Column(String, nullable=False)  # argon2 (argon2-cffi) hash
    birthdate = Column(Date, nullable=False)
    gender = Column(Enum(GenderEnum, name="gender_enum"), nullable=False)
    res_area = Column(String(50), nullable=False)
    is_admin = Column(Boolean, nullable=False)
    store_id = Column(BigInteger)
    store_role = Column(Enum(StoreRoleEnum, name="store_role_enum"))
    email_verified = Column(
        Boolean, nullable=False, default=False
    )  # email verification

    # Relationships
    order = relationship("Order", back_populates="user")
    sale = relationship("Sale", back_populates="user")
    review = relationship("Review", back_populates="user")
    points = relationship("Points", back_populates="user")
    verification_codes = relationship(
        "VerificationCode", back_populates="user", cascade="all, delete-orphan"
    )
