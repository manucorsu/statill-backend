import enum

from ..database.base import Base

from sqlalchemy import Column, BigInteger, ForeignKey, String, DateTime, func, Enum
from sqlalchemy.orm import relationship


class VerificationCodeType(str, enum.Enum):
    EMAIL = "email"
    STORE_ADD = "store_add"
    PASSWORD_RESET = "password_reset"


class VerificationCode(Base):
    __tablename__ = "verification_codes"

    id = Column(BigInteger, primary_key=True)
    user_id = Column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    type = Column(
        Enum(VerificationCodeType, name="verification_code_type_enum"), nullable=False
    )
    code = Column(String(64), nullable=False, unique=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="verification_codes")
