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
    db.insert_exchange_rate(data['exchange_rate'])

    print(f"[{datetime.now()}] Data update completed!")


def start_scheduler():
    """Start the background scheduler"""
    scheduler = BackgroundScheduler()

    # Run every day at midnight
    scheduler.add_job(
        func=update_economic_data,
        trigger='cron',
        hour=0,
        minute=0,
        id='daily_update',
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
