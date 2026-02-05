"""
Database Module
Handles all PostgreSQL database operations
"""

import os
import psycopg2
from psycopg2.extras import execute_values
import pandas as pd


class EconomicDatabase:
    """Handle all database operations"""

    def __init__(self):
        self.db_url = os.getenv('DATABASE_URL', 'postgresql://egyptecon:egyptecon_pass@localhost:5432/egyptecon')
        self.conn = None

    def connect(self):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(self.db_url)
            return True
        except Exception as e:
            print(f"Database connection error: {e}")
            return False

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None

    def create_tables(self):
        """Create tables if they don't exist"""
        if not self.connect():
            return False

        try:
            cursor = self.conn.cursor()

            # GDP table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS gdp_data (
                    id SERIAL PRIMARY KEY,
                    date DATE UNIQUE NOT NULL,
                    gdp_billions_usd DECIMAL(12, 2),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Inflation table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS inflation_data (
                    id SERIAL PRIMARY KEY,
                    date DATE UNIQUE NOT NULL,
                    inflation_rate DECIMAL(8, 2),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Exchange rate table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS exchange_rate_data (
                    id SERIAL PRIMARY KEY,
                    date DATE UNIQUE NOT NULL,
                    usd_egp_rate DECIMAL(10, 2),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            self.conn.commit()
            cursor.close()
            print("Tables created successfully!")
            return True

        except Exception as e:
            print(f"Error creating tables: {e}")
            self.conn.rollback()
            return False
        finally:
            self.close()

    def insert_gdp_data(self, df):
        """Insert GDP data from DataFrame"""
        if df is None or df.empty:
            return

        if not self.connect():
            return

        try:
            cursor = self.conn.cursor()
            values = [(row['date'], row['gdp_billions_usd']) for _, row in df.iterrows()]

            execute_values(cursor, """
                INSERT INTO gdp_data (date, gdp_billions_usd)
                VALUES %s
                ON CONFLICT (date) DO UPDATE
                SET gdp_billions_usd = EXCLUDED.gdp_billions_usd
            """, values)

            self.conn.commit()
            cursor.close()
            print(f"Inserted {len(values)} GDP records")

        except Exception as e:
            print(f"Error inserting GDP data: {e}")
            self.conn.rollback()
        finally:
            self.close()

    def insert_inflation_data(self, df):
        """Insert inflation data from DataFrame"""
        if df is None or df.empty:
            return

        if not self.connect():
            return

        try:
            cursor = self.conn.cursor()
            values = [(row['date'], row['inflation_rate']) for _, row in df.iterrows()]

            execute_values(cursor, """
                INSERT INTO inflation_data (date, inflation_rate)
                VALUES %s
                ON CONFLICT (date) DO UPDATE
                SET inflation_rate = EXCLUDED.inflation_rate
            """, values)

            self.conn.commit()
            cursor.close()
            print(f"Inserted {len(values)} inflation records")

        except Exception as e:
            print(f"Error inserting inflation data: {e}")
            self.conn.rollback()
        finally:
            self.close()

    def insert_exchange_rate(self, data):
        """Insert single exchange rate record"""
        if not data:
            return

        if not self.connect():
            return

        try:
            cursor = self.conn.cursor()

            cursor.execute("""
                INSERT INTO exchange_rate_data (date, usd_egp_rate)
                VALUES (%s, %s)
                ON CONFLICT (date) DO UPDATE
                SET usd_egp_rate = EXCLUDED.usd_egp_rate
            """, (data['date'], data['usd_egp_rate']))

            self.conn.commit()
            cursor.close()
            print("Inserted exchange rate")

        except Exception as e:
            print(f"Error inserting exchange rate: {e}")
            self.conn.rollback()
        finally:
            self.close()

    def get_all_gdp(self):
        """Retrieve all GDP data"""
        if not self.connect():
            return pd.DataFrame()

        try:
            df = pd.read_sql("SELECT date, gdp_billions_usd FROM gdp_data ORDER BY date", self.conn)
            return df
        except Exception as e:
            print(f"Error retrieving GDP data: {e}")
            return pd.DataFrame()
        finally:
            self.close()

    def get_all_inflation(self):
        """Retrieve all inflation data"""
        if not self.connect():
            return pd.DataFrame()

        try:
            df = pd.read_sql("SELECT date, inflation_rate FROM inflation_data ORDER BY date", self.conn)
            return df
        except Exception as e:
            print(f"Error retrieving inflation data: {e}")
            return pd.DataFrame()
        finally:
            self.close()

    def get_all_exchange_rates(self):
        """Retrieve all exchange rate data"""
        if not self.connect():
            return pd.DataFrame()

        try:
            df = pd.read_sql("SELECT date, usd_egp_rate FROM exchange_rate_data ORDER BY date", self.conn)
            return df
        except Exception as e:
            print(f"Error retrieving exchange rate data: {e}")
            return pd.DataFrame()
        finally:
            self.close()

    def get_latest_data(self):
        """Get latest values for all indicators"""
        gdp_df = self.get_all_gdp()
        inflation_df = self.get_all_inflation()
        exchange_df = self.get_all_exchange_rates()

        return {
            'gdp': gdp_df.iloc[-1].to_dict() if not gdp_df.empty else None,
            'inflation': inflation_df.iloc[-1].to_dict() if not inflation_df.empty else None,
            'exchange_rate': exchange_df.iloc[-1].to_dict() if not exchange_df.empty else None
        }


if __name__ == "__main__":
    db = EconomicDatabase()
    db.create_tables()

    # Test with sample data
    from data_fetcher import EconomicDataFetcher
    fetcher = EconomicDataFetcher()
    data = fetcher.fetch_all_data()

    db.insert_gdp_data(data['gdp'])
    db.insert_inflation_data(data['inflation'])
    db.insert_exchange_rate(data['exchange_rate'])

    print("\nRetrieved GDP data:")
    print(db.get_all_gdp().tail())
