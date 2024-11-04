import random
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_, update
from models.user import user, account, trading, assets_pairs
from router.user_routes.helpers import account_task
from database import SessionLocal
from decimal import Decimal


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def auto_trade_bot(db: Session):
    try:
        def get_random_asset_pair():
            asset_pair = db.query(assets_pairs.AssetPair).all()
            number = random.randint(0, len(asset_pair))
            chosen_pair = asset_pair[number].asset_pair
            return chosen_pair

        users_update = db.query(user.User).all()
        # for user__ in users_update:
        #     user__.auto_trade_count = 0
        #     db.commit()
        #     db.refresh(user__)
        # print("Auto Trade Count is set to 0")

        users = db.query(user.User).filter(and_(user.User.can_auto_trade, user.User.user_type == "customer")).all()
        if users:
            for user_ in users:
                get_account = db.query(account.Account).filter(account.Account.user_id == user_.id).first()
                get_count = user_.auto_trade_count

                async def create_trade(limit: float, minimum_amount: float):
                    if minimum_amount > get_account.main_balance:
                        minimum_amount = Decimal(get_account.main_balance / 2)
                    minimum_amount = min(minimum_amount, Decimal(get_account.main_balance))
                    if minimum_amount > get_account.main_balance:
                        raise ValueError("Minimum amount exceeds main balance")
                    amount_to_trade = random.uniform(minimum_amount, get_account.main_balance)
                    if amount_to_trade < minimum_amount:
                        return  # Skip trade if amount to trade is less than minimum
                    if get_account.main_balance > limit:
                        debit = await account_task(task="create", amount=Decimal(amount_to_trade), user_id=user_.id,
                                                   db=db)
                        if debit['status'] == 'success':
                            trading_ = trading.TradeTable(
                                user_id=user_.id,
                                asset_pair_type=get_random_asset_pair(),
                                trade_type=random.choice(['limit', 'market']),
                                amount=Decimal(amount_to_trade),
                                created_by='auto-trader',
                                status='open',
                                trade_transaction_type=random.choice(['buy', 'sell'])
                            )
                            user_.auto_trade_count += 1
                            db.add(trading_)
                            db.commit()
                            print(
                                f"Trading for {user_.first_name, user_.last_name} with email {user_.email} is opened with amount {trading_.amount}")
                        else:
                            db.rollback()
                            print("Error debiting account")
                    else:
                        print("Unable to open Trade for ", user_.first_name)

                async def close_trade(trade_id: int):
                    query = db.query(trading.TradeTable).filter(trading.TradeTable.id == trade_id).first()
                    # amount_profit = int(((query.profit / 100) * query.amount)) + query.amount
                    to_profit = round(random.uniform(5.0, 11.0), 2)
                    amount_profit = Decimal((Decimal(to_profit / 100) * Decimal(query.amount))) + Decimal(query.amount)
                    print(amount_profit)
                    if query.status != "closed":
                        print("old_balance ", get_account.main_balance)
                        get_account.main_balance = get_account.main_balance + amount_profit
                        query.profit = to_profit
                        query.status = "closed"
                        db.commit()
                        db.refresh(get_account)
                        print("new_balance ", get_account.main_balance)
                    else:
                        print("Unable to close Trade")

                to_open_or_close = random.choice(["open", "close"])
                check_closed_trade = db.query(trading.TradeTable).filter(
                    and_(trading.TradeTable.user_id == user_.id, trading.TradeTable.status == 'open')).first()

                match get_account.account_type:
                    case "basic":
                        match to_open_or_close:
                            case 'open':
                                if get_count <= 2:
                                    await create_trade(50, 20)
                            case 'close':
                                if check_closed_trade:
                                    await close_trade(check_closed_trade.id)
                    case "premium":
                        match to_open_or_close:
                            case 'open':
                                if get_count <= 7:
                                    await create_trade(50, 30)
                            case 'close':
                                if check_closed_trade:
                                    await close_trade(check_closed_trade.id)
                    case 'gold':
                        match to_open_or_close:
                            case 'open':
                                if get_count <= 12:
                                    await create_trade(300, 50)
                            case 'close':
                                if check_closed_trade:
                                    await close_trade(check_closed_trade.id)
                    case 'platinum':
                        match to_open_or_close:
                            case 'open':
                                if get_count <= 15:
                                    await create_trade(700, 100)
                            case 'close':
                                if check_closed_trade:
                                    await close_trade(check_closed_trade.id)
                    case _:
                        print("no user")
        else:
            print("No user can auto trade")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=401, detail=str(e))


async def reset_auto_trade_count(db: Session):
    accounts = db.query(account.Account).filter(account.Account.account_type != 'basic').all()
    for account_ in accounts:
        user_ = db.query(user.User).filter(user.User == account_.user_id).first()
        user_.auto_trade_count = 0
        db.commit()


async def auto_trade_bot_wrapper():
    db = next(get_db())
    await auto_trade_bot(db)


async def reset_count_function():
    db = next(get_db())
    await reset_auto_trade_count(db)
