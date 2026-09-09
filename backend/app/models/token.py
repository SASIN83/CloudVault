from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.database import Base


class RevokedToken(Base):
    """Denylist of logged-out JWTs, kept only until their natural expiry."""
    __tablename__ = "revoked_tokens"

    id = Column(Integer, primary_key=True)
    jti = Column(String, unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    revoked_at = Column(DateTime, default=datetime.utcnow)