from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal, engine
from dependencies import get_token_header
from .trader_class import TraderClass
from models.user import trading
from models.user.assets_pairs import AssetPair
from schema.trading import TradeTableCreate

trading.Base.metadata.create_all(bind=engine)

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/get-assets")
async def get_assets(token_payload: dict = Depends(get_token_header), db: Session = Depends(get_db)):
    if token_payload:
        return db.query(AssetPair).all()


@router.get("/get-all-trade/")
async def get_all_trade(token_payload: dict = Depends(get_token_header), db: Session = Depends(get_db)):
    user_id = token_payload.get("data")
    trade_ = TraderClass(db, user_id)
    trades_ = trade_.get_all_trade()
    if trades_:
        return [{"status": "success"}, {"data": trades_}]
    else:
        raise HTTPException(status_code=404, detail="Unable to get trade")


@router.get("/auto-trade/")
async def change_auto_trade_status(token_payload: dict = Depends(get_token_header),
                                   db: Session = Depends(get_db)):
    user_id = token_payload.get("data")
    auto_trade_ = TraderClass(db, user_id)
    auto_trades_ = auto_trade_.activate_auto_trader()
    if auto_trades_:
        return auto_trades_
    else:
        raise HTTPException(status_code=404, detail="Unable to open trade")


@router.post("/open-trade/")
async def open_trade(trading_data: TradeTableCreate, token_payload: dict = Depends(get_token_header),
                     db: Session = Depends(get_db)):
    try:
        user_id = token_payload.get("data")
        trade_ = TraderClass(db, user_id)
        trades_ = await trade_.create_trade(trading_data)
        if trades_:
            return [{"status": "success"}, {"data": trades_}]
        else:
            raise HTTPException(status_code=404, detail="Unable to close trade")
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Unable to open trade {e}")


@router.post("/close-trade/{trade_id}")
async def close_trade(trade_id: int, token_payload: dict = Depends(get_token_header),
                      db: Session = Depends(get_db)):
    try:
        user_id = token_payload.get("data")
        trade_ = TraderClass(db, user_id)
        trades_ = await trade_.close_trade(trade_id=trade_id)
        if trades_:
            return [{"status": "success"}, {"data": trades_}]
        else:
            raise HTTPException(status_code=404, detail="Unable to close trade")
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Unable to close trade {e}")
