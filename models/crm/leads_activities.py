from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class CRMUserActivities(Base):
    __tablename__ = "crm_user_activities"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("crm_user_base.id"))
    comment = Column(String(255))
    created_at = Column(DateTime, default=datetime.now())

    crm_user_base = relationship("CRMUserBase", back_populates="crm_user_activities")
