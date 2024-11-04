from pydantic import BaseModel
from enum import Enum


class AssetTypeEnum(str, Enum):
    cryptocurrency = "cryptocurrency"
    stocks = "stocks"
    indices = "indices"
    forex = "forex"


class AssetBase(BaseModel):
    asset_pair: str
    asset_url: str
    asset_type: AssetTypeEnum


class Asset(AssetBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True
