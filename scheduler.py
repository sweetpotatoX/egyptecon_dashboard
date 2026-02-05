"""
Scheduler Module
Handles automated daily data updates using APScheduler
"""

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime


def update_economic_data():
    """Fetch fresh data and update database"""
    print(f"[{datetime.now()}] Starting scheduled data update...")

    # Import here to avoid circular imports
    from data_fetcher import EconomicDataFetcher
    from database import EconomicDatabase

    fetcher = EconomicDataFetcher()
    db = EconomicDatabase()

    # Ensure tables exist
    db.create_tables()

    # Fetch all data
    data = fetcher.fetch_all_data()

    # Update database
    db.insert_gdp_data(data['gdp'])
    db.insert_inflation_data(data['inflation'])
    db.insert_exchange_rate_history(data['exchange_rate_history'])
    db.insert_exchange_rate(data['exchange_rate_latest'])
    db.insert_egx30_history(data['egx30_history'])
    db.insert_egx30_latest(data['egx30_latest'])

    print(f"[{datetime.now()}] Data update completed!")


def update_market_data_only():
    """Fetch latest market data (USD/EGP) and update database"""
    print(f"[{datetime.now()}] Updating latest market data...")

    from data_fetcher import EconomicDataFetcher
    from database import EconomicDatabase

    fetcher = EconomicDataFetcher()
    db = EconomicDatabase()

    db.create_tables()
    latest_fx = fetcher.fetch_exchange_rate()
    db.insert_exchange_rate(latest_fx)

    print(f"[{datetime.now()}] Latest market data updated!")


def start_scheduler():
    """Start the background scheduler"""
    scheduler = BackgroundScheduler()

    # Run full refresh every day at midnight
    scheduler.add_job(
        func=update_economic_data,
        trigger='cron',
        hour=0,
        minute=0,
        id='daily_update',
        replace_existing=True
    )

    # Update market data every minute
    scheduler.add_job(
        func=update_market_data_only,
        trigger='interval',
        minutes=1,
        id='minute_exchange_update',
        replace_existing=True
    )

    # Run once immediately on startup
    scheduler.add_job(
        func=update_economic_data,
        trigger='date',
        id='initial_update',
        replace_existing=True
    )

    scheduler.start()
    print("Scheduler started! Data will update daily at midnight.")

    return scheduler


if __name__ == "__main__":
    scheduler = start_scheduler()

    # Keep script running
    try:
        import time
        while True:
            time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        print("Scheduler stopped.")
