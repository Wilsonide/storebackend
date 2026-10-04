import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID

from app.db.database import Base


class Token(Base):
    __tablename__ = "tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    token_hash = Column(String, nullable=False, unique=True)

    expires_at = Column(DateTime, nullable=False)

    used = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
