from sqlalchemy import Column, String, Enum, Integer, Date, Boolean, BigInteger
from datetime import datetime
from sqlalchemy.orm import relationship

from database import Base


class CRMUserBase(Base):
    __tablename__ = "crm_user_base"

    id = Column(Integer, primary_key=True)
    email = Column(String(255))
    first_name = Column(String(255))
    last_name = Column(String(255))
    address = Column(String(255))
    country = Column(String(255))
    phone_number = Column(BigInteger)
    date_of_birth = Column(Date)
    status = Column(Enum('Not Called', 'Unavailable', 'Call back', 'Not Interested',  name='status_type_enum'), default="Not Called")
    activated = Column(Boolean, default=False)
    assigned_to = Column(Integer)
    created_at = Column(Date, default=datetime.now())

    crm_user_activities = relationship("CRMUserActivities", uselist=False, back_populates="crm_user_base")
