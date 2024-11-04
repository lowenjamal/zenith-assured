from sqlalchemy import Column, Enum, Integer, ForeignKey, String, Boolean
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import relationship

from database import Base


class AssetPair(Base):
    __tablename__ = "assets_pair"
    id = Column(Integer, primary_key=True)
    asset_pair = Column(String(255))
    asset_url = Column(String(255))
    asset_type = Column(Enum('cryptocurrency', 'stocks', 'indices', 'forex', name='asset_type_enum'))
    is_active = Column(Boolean, default=True)


