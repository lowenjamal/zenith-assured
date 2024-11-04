from sqlalchemy import Column, Enum, Integer, ForeignKey, DateTime, DECIMAL, String, Boolean
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


class DocumentVerification(Base):
    __tablename__ = "document_verifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    front_document_path = Column(String, index=True)
    back_document_path = Column(String, index=True, nullable=True)
    created_at = Column(DateTime, default=datetime.now())

    user = relationship("User", back_populates="document_verifications")
