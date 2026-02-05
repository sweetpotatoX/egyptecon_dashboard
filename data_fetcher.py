"""
Economic Data Fetcher
Fetches GDP, inflation, and exchange rate data from public APIs
"""

import requests
import pandas as pd
from datetime import datetime


class EconomicDataFetcher:
    """Fetch economic data from various APIs"""

    def __init__(self):
        self.world_bank_base = "https://api.worldbank.org/v2/country/EG/indicator"
        self.exchange_base = "https://api.exchangerate.host/latest"
        self.start_year = 1980  # Data starts from 1980s

    def fetch_gdp(self, years=None):
        """
        Fetch GDP data from World Bank (monthly frequency)
        Returns: DataFrame with columns [date, gdp_billions_usd]
        """
        if years is None:
            years = datetime.now().year - self.start_year + 1
        
        url = f"{self.world_bank_base}/NY.GDP.MKTP.CD"
        params = {
            'format': 'json',
            'per_page': 1000,  # Increased to accommodate monthly data
            'date': f'{self.start_year}:{datetime.now().year}',
            'frequency': 'M'  # Monthly frequency
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if len(data) < 2 or data[1] is None:
                print("No GDP data returned from API")
                return pd.DataFrame()

            records = []
            for item in data[1]:
                if item['value'] is not None:
                    # Parse date - handle both annual (YYYY) and monthly (YYYYMXX) formats
                    date_str = item['date']
                    if 'M' in date_str:  # Monthly format: "2023M01"
                        year, month = date_str.split('M')
                        date_obj = datetime(int(year), int(month), 1)
                    else:  # Annual format: "2023"
                        date_obj = datetime(int(date_str), 1, 1)
                    
                    records.append({
                        'date': date_obj,
                        'gdp_billions_usd': round(float(item['value']) / 1e9, 2)
                    })

            df = pd.DataFrame(records)
            df = df.sort_values('date')
            return df

        except Exception as e:
            print(f"Error fetching GDP: {e}")
            return pd.DataFrame()

    def fetch_inflation(self, years=None):
        """
        Fetch inflation rate from World Bank (monthly frequency)
        Returns: DataFrame with columns [date, inflation_rate]
        """
        if years is None:
            years = datetime.now().year - self.start_year + 1
        
        url = f"{self.world_bank_base}/FP.CPI.TOTL.ZG"
        params = {
            'format': 'json',
            'per_page': 1000,  # Increased to accommodate monthly data
            'date': f'{self.start_year}:{datetime.now().year}',
            'frequency': 'M'  # Monthly frequency
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if len(data) < 2 or data[1] is None:
                print("No inflation data returned from API")
                return pd.DataFrame()

            records = []
            for item in data[1]:
                if item['value'] is not None:
                    # Parse date - handle both annual (YYYY) and monthly (YYYYMXX) formats
                    date_str = item['date']
                    if 'M' in date_str:  # Monthly format: "2023M01"
                        year, month = date_str.split('M')
                        date_obj = datetime(int(year), int(month), 1)
                    else:  # Annual format: "2023"
                        date_obj = datetime(int(date_str), 1, 1)
                    
                    records.append({
                        'date': date_obj,
                        'inflation_rate': round(float(item['value']), 2)
                    })

            df = pd.DataFrame(records)
            df = df.sort_values('date')
            return df

        except Exception as e:
            print(f"Error fetching inflation: {e}")
            return pd.DataFrame()

    def fetch_exchange_rate_history(self):
        """
        Fetch historical USD/EGP exchange rate from World Bank (annual)
        Returns: DataFrame with columns [date, usd_egp_rate]
        """
        url = f"{self.world_bank_base}/PA.NUS.FCRF"
        params = {
            'format': 'json',
            'per_page': 1000,
            'date': f'{self.start_year}:{datetime.now().year}'
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if len(data) < 2 or data[1] is None:
                print("No exchange rate history returned from API")
                return pd.DataFrame()

            records = []
            for item in data[1]:
                if item['value'] is not None:
                    date_obj = datetime(int(item['date']), 1, 1)
                    records.append({
                        'date': date_obj,
                        'usd_egp_rate': round(float(item['value']), 4)
                    })

            df = pd.DataFrame(records)
            df = df.sort_values('date')
            return df

        except Exception as e:
            print(f"Error fetching exchange rate history: {e}")
            return pd.DataFrame()

    def fetch_exchange_rate(self):
        """
        Fetch current USD/EGP exchange rate (latest)
        Returns: Dictionary with {date, usd_egp_rate}
        """
        try:
            params = {
                'base': 'USD',
                'symbols': 'EGP'
            }
            response = requests.get(self.exchange_base, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            egp_rate = data.get('rates', {}).get('EGP')
            if egp_rate:
                return {
                    'date': datetime.now().replace(hour=0, minute=0, second=0, microsecond=0),
                    'usd_egp_rate': round(float(egp_rate), 2)
                }
            return None

        except Exception as e:
            print(f"Error fetching exchange rate: {e}")
            return None

    def fetch_all_data(self):
        """
        Fetch all economic indicators
        Returns: Dictionary with DataFrames for each indicator
        """
        return {
            'gdp': self.fetch_gdp(),
            'inflation': self.fetch_inflation(),
            'exchange_rate_history': self.fetch_exchange_rate_history(),
            'exchange_rate_latest': self.fetch_exchange_rate()
        }


if __name__ == "__main__":
    fetcher = EconomicDataFetcher()
    data = fetcher.fetch_all_data()

    print("GDP Data:")
    print(data['gdp'].head() if not data['gdp'].empty else "No data")
    print("\nInflation Data:")
    print(data['inflation'].head() if not data['inflation'].empty else "No data")
    print("\nExchange Rate:")
    print(data['exchange_rate_latest'])
