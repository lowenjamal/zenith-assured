from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import requests
from database import SessionLocal, engine

from models.user.assets_pairs import AssetPair
from schema.asset_pair import AssetTypeEnum

router = APIRouter()


# assets_pairs.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Add forex and others later.
@router.get("/create-asset/")
async def create_asset(key: str, db: Session = Depends(get_db)):
    try:
        if key != "The Devil Is Born":
            raise HTTPException(status_code=401, detail="You are not allowed to use this route Ever again!!!")
        else:
            response = requests.get("https://api.binance.com/api/v3/exchangeInfo")
            if response.status_code == 200:
                data = response.json()
                for item in data['symbols']:
                    asset_pair_name = item['symbol']
                    asset_url = f"https://api.binance.com/api/v3/ticker/price?symbol={asset_pair_name}"
                    asset_pair_entry = AssetPair(
                        asset_pair=asset_pair_name,
                        asset_url=asset_url,
                        asset_type=AssetTypeEnum.cryptocurrency,
                    )
                    db.add(asset_pair_entry)
                db.commit()
                return {"status": "success"}
            else:
                raise HTTPException(status_code=response.status_code, detail=response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
