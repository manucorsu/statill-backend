from ..database.base import Base

from sqlalchemy import Column, BigInteger, ForeignKey, String, DateTime, func
from sqlalchemy.orm import relationship


class EmailVerificationCode(Base):
    __tablename__ = "email_verification_codes"

    id = Column(BigInteger, primary_key=True)
    user_id = Column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    code = Column(String(64), nullable=False, unique=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="verification_codes")
