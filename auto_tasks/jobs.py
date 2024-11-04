from apscheduler.schedulers.asyncio import AsyncIOScheduler
from auto_tasks.auto_trader import auto_trade_bot_wrapper, reset_count_function
scheduler = AsyncIOScheduler()

scheduler.add_job(reset_count_function, 'cron', hour=0)
scheduler.add_job(auto_trade_bot_wrapper, 'interval', seconds=60*60)