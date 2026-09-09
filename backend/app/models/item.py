from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Item(Base):
    """Represents both files and folders (hierarchical via parent_id)."""
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    is_folder = Column(Boolean, default=False)
    size = Column(Integer, default=0)                          # bytes
    s3_key = Column(String, unique=True, nullable=True)        # AWS S3 object key
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)               # soft-delete (Trash)

    parent_id = Column(Integer, ForeignKey("items.id"), nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    owner = relationship("User")
    shares = relationship("ItemShare", back_populates="item", cascade="all, delete-orphan")


class ItemShare(Base):
    """Email-based sharing. Only a signed-in user with this exact email gets access."""
    __tablename__ = "item_shares"

    id = Column(Integer, primary_key=True)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    shared_email = Column(String, nullable=False, index=True)

    item = relationship("Item", back_populates="shares")