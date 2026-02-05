# PROJECT IMPLEMENTATION GUIDES
## For: Abdelrahman Bahaa

---

# PROJECT 1: EGYPTECON DASHBOARD

## PROJECT OVERVIEW

**What You're Building:**
A real-time economic data dashboard that automatically scrapes data from government APIs, stores it in PostgreSQL, visualizes trends using interactive charts, and generates PDF reports.

**Final Product:**
- Live web dashboard at a public URL (e.g., egyptecon.herokuapp.com)
- Updates automatically every day at midnight
- Shows Egypt's GDP, inflation rate, and USD/EGP exchange rate
- Interactive charts you can zoom/pan
- "Download PDF Report" button

**Time to Build:** 25-30 hours over 2 weeks

---

## TECH STACK

### Core Technologies:
1. **Python 3.9+** - Programming language
2. **Plotly Dash** - Web framework for dashboards
3. **PostgreSQL** - Database to store historical data
4. **Pandas** - Data manipulation
5. **Requests** - API calls
6. **APScheduler** - Scheduling daily updates (instead of cron)
7. **ReportLab** - PDF generation
8. **Heroku or Railway** - Deployment platform (free tier)

### Why These Technologies?

- **Plotly Dash** - Easier than building separate frontend/backend; Python-only
- **PostgreSQL** - Free on Heroku/Railway, handles time-series data well
- **APScheduler** - Works on Windows/Mac/Linux (cron only works on Linux)
- **Heroku/Railway** - Free hosting with PostgreSQL add-on

---

## STEP-BY-STEP IMPLEMENTATION

### PHASE 1: PROJECT SETUP (2-3 hours)

#### Step 1.1: Install Python and Tools

```bash
# Check Python version (need 3.9+)
python --version

# Create project folder
mkdir egyptecon-dashboard
cd egyptecon-dashboard

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install required packages
pip install dash plotly pandas psycopg2-binary requests apscheduler reportlab python-dotenv
pip freeze > requirements.txt
```

#### Step 1.2: Set Up PostgreSQL Locally

**Option A: Install PostgreSQL on Your Machine**

1. Download from: https://www.postgresql.org/download/
2. Install with default settings
3. Remember your password!
4. Open pgAdmin or use terminal:

```bash
# Create database
psql -U postgres
CREATE DATABASE egyptecon;
\q
```

**Option B: Use Docker (Easier)**

```bash
# Install Docker Desktop first: https://www.docker.com/products/docker-desktop

# Run PostgreSQL in container
docker run --name egyptecon-db -e POSTGRES_PASSWORD=mypassword -e POSTGRES_DB=egyptecon -p 5432:5432 -d postgres

# Access it
docker exec -it egyptecon-db psql -U postgres -d egyptecon
```

#### Step 1.3: Project Structure

Create this folder structure:

```
egyptecon-dashboard/
├── app.py                 # Main Dash application
├── data_fetcher.py        # Fetch data from APIs
├── database.py            # Database connection & queries
├── scheduler.py           # Daily update scheduler
├── pdf_generator.py       # Generate PDF reports
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (don't commit!)
├── .gitignore            # Git ignore file
├── Procfile              # For Heroku deployment
└── README.md             # Documentation
```

---

### PHASE 2: DATA FETCHING (4-5 hours)

#### Step 2.1: Find APIs

**Problem:** Egypt Central Bank doesn't have a public API. Here's what to use instead:

**Data Sources:**
1. **World Bank API** - GDP, inflation
   - URL: https://api.worldbank.org/v2/country/EG/indicator/
   - Free, no API key needed

2. **Exchange Rates API** - USD/EGP rate
   - URL: https://api.exchangerate-api.com/v4/latest/USD
   - Free tier available

3. **Alternative:** Alpha Vantage (free tier, needs API key)
   - URL: https://www.alphavantage.co/

#### Step 2.2: Create `data_fetcher.py`

```python
import requests
import pandas as pd
from datetime import datetime, timedelta

class EconomicDataFetcher:
    """Fetch economic data from various APIs"""
    
    def __init__(self):
        self.world_bank_base = "https://api.worldbank.org/v2/country/EG/indicator"
        self.exchange_base = "https://api.exchangerate-api.com/v4/latest/USD"
    
    def fetch_gdp(self, years=10):
        """
        Fetch GDP data from World Bank
        Returns: DataFrame with columns [date, gdp_billions_usd]
        """
        # World Bank indicator code for GDP: NY.GDP.MKTP.CD
        url = f"{self.world_bank_base}/NY.GDP.MKTP.CD"
        params = {
            'format': 'json',
            'per_page': years,
            'date': f'{datetime.now().year-years}:{datetime.now().year}'
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # World Bank returns [metadata, data]
            if len(data) < 2:
                return pd.DataFrame()
            
            records = []
            for item in data[1]:
                if item['value'] is not None:
                    records.append({
                        'date': datetime(int(item['date']), 1, 1),
                        'gdp_billions_usd': round(float(item['value']) / 1e9, 2)  # Convert to billions
                    })
            
            df = pd.DataFrame(records)
            df = df.sort_values('date')
            return df
            
        except Exception as e:
            print(f"Error fetching GDP: {e}")
            return pd.DataFrame()
    
    def fetch_inflation(self, years=10):
        """
        Fetch inflation rate from World Bank
        Returns: DataFrame with columns [date, inflation_rate]
        """
        # World Bank indicator code for inflation: FP.CPI.TOTL.ZG
        url = f"{self.world_bank_base}/FP.CPI.TOTL.ZG"
        params = {
            'format': 'json',
            'per_page': years,
            'date': f'{datetime.now().year-years}:{datetime.now().year}'
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if len(data) < 2:
                return pd.DataFrame()
            
            records = []
            for item in data[1]:
                if item['value'] is not None:
                    records.append({
                        'date': datetime(int(item['date']), 1, 1),
                        'inflation_rate': round(float(item['value']), 2)
                    })
            
            df = pd.DataFrame(records)
            df = df.sort_values('date')
            return df
            
        except Exception as e:
            print(f"Error fetching inflation: {e}")
            return pd.DataFrame()
    
    def fetch_exchange_rate(self):
        """
        Fetch current USD/EGP exchange rate
        Returns: Dictionary with {date, usd_egp_rate}
        """
        try:
            response = requests.get(self.exchange_base, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            egp_rate = data['rates'].get('EGP')
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
            'exchange_rate': self.fetch_exchange_rate()
        }


# Test the fetcher
if __name__ == "__main__":
    fetcher = EconomicDataFetcher()
    data = fetcher.fetch_all_data()
    
    print("GDP Data:")
    print(data['gdp'].head())
    print("\nInflation Data:")
    print(data['inflation'].head())
    print("\nExchange Rate:")
    print(data['exchange_rate'])
```

**Run this to test:**
```bash
python data_fetcher.py
```

You should see data printed. If you get errors, the APIs might be down or require authentication.

---

### PHASE 3: DATABASE SETUP (3-4 hours)

#### Step 3.1: Create `.env` File

```bash
# .env file - NEVER commit this to Git
DATABASE_URL=postgresql://postgres:mypassword@localhost:5432/egyptecon
```

#### Step 3.2: Create `database.py`

```python
import psycopg2
from psycopg2.extras import execute_values
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

class EconomicDatabase:
    """Handle all database operations"""
    
    def __init__(self):
        self.db_url = os.getenv('DATABASE_URL')
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
        if df.empty:
            return
        
        if not self.connect():
            return
        
        try:
            cursor = self.conn.cursor()
            
            # Convert DataFrame to list of tuples
            values = [(row['date'], row['gdp_billions_usd']) for _, row in df.iterrows()]
            
            # Insert with ON CONFLICT to handle duplicates
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
        if df.empty:
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


# Initialize database
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
```

**Run this to initialize database:**
```bash
python database.py
```

---

### PHASE 4: BUILD DASHBOARD (6-8 hours)

#### Step 4.1: Create `app.py` (Main Dashboard)

```python
import dash
from dash import dcc, html, Input, Output, State
import plotly.graph_objs as go
import pandas as pd
from database import EconomicDatabase

# Initialize Dash app
app = dash.Dash(__name__)
server = app.server  # For deployment

# Initialize database
db = EconomicDatabase()

# App layout
app.layout = html.Div([
    # Header
    html.Div([
        html.H1("Egypt Economic Dashboard", 
                style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': 10}),
        html.P("Real-time economic indicators for Egypt", 
               style={'textAlign': 'center', 'color': '#7f8c8d', 'fontSize': 18}),
    ], style={'padding': '20px'}),
    
    # Refresh button and last update
    html.Div([
        html.Button('Refresh Data', id='refresh-button', n_clicks=0,
                    style={'marginRight': 20, 'padding': '10px 20px', 'fontSize': 16}),
        html.Button('Download PDF Report', id='pdf-button', n_clicks=0,
                    style={'padding': '10px 20px', 'fontSize': 16}),
        html.Div(id='last-update', style={'marginTop': 10, 'fontStyle': 'italic'})
    ], style={'textAlign': 'center', 'marginBottom': 30}),
    
    # GDP Chart
    html.Div([
        html.H3("GDP (Billions USD)", style={'color': '#34495e'}),
        dcc.Graph(id='gdp-chart')
    ], style={'marginBottom': 40}),
    
    # Inflation Chart
    html.Div([
        html.H3("Inflation Rate (%)", style={'color': '#34495e'}),
        dcc.Graph(id='inflation-chart')
    ], style={'marginBottom': 40}),
    
    # Exchange Rate Chart
    html.Div([
        html.H3("USD/EGP Exchange Rate", style={'color': '#34495e'}),
        dcc.Graph(id='exchange-chart')
    ], style={'marginBottom': 40}),
    
    # Interval component for auto-refresh (every 24 hours = 86400000 ms)
    dcc.Interval(id='interval-component', interval=86400000, n_intervals=0),
    
    # Hidden div to store data
    html.Div(id='hidden-div', style={'display': 'none'})
])


@app.callback(
    [Output('gdp-chart', 'figure'),
     Output('inflation-chart', 'figure'),
     Output('exchange-chart', 'figure'),
     Output('last-update', 'children')],
    [Input('interval-component', 'n_intervals'),
     Input('refresh-button', 'n_clicks')]
)
def update_charts(n_intervals, n_clicks):
    """Update all charts with latest data from database"""
    
    # Fetch data from database
    gdp_df = db.get_all_gdp()
    inflation_df = db.get_all_inflation()
    exchange_df = db.get_all_exchange_rates()
    
    # GDP Chart
    gdp_fig = go.Figure()
    if not gdp_df.empty:
        gdp_fig.add_trace(go.Scatter(
            x=gdp_df['date'],
            y=gdp_df['gdp_billions_usd'],
            mode='lines+markers',
            name='GDP',
            line=dict(color='#3498db', width=3),
            marker=dict(size=8)
        ))
    gdp_fig.update_layout(
        xaxis_title="Year",
        yaxis_title="GDP (Billions USD)",
        hovermode='x unified',
        template='plotly_white'
    )
    
    # Inflation Chart
    inflation_fig = go.Figure()
    if not inflation_df.empty:
        inflation_fig.add_trace(go.Scatter(
            x=inflation_df['date'],
            y=inflation_df['inflation_rate'],
            mode='lines+markers',
            name='Inflation Rate',
            line=dict(color='#e74c3c', width=3),
            marker=dict(size=8)
        ))
    inflation_fig.update_layout(
        xaxis_title="Year",
        yaxis_title="Inflation Rate (%)",
        hovermode='x unified',
        template='plotly_white'
    )
    
    # Exchange Rate Chart
    exchange_fig = go.Figure()
    if not exchange_df.empty:
        exchange_fig.add_trace(go.Scatter(
            x=exchange_df['date'],
            y=exchange_df['usd_egp_rate'],
            mode='lines+markers',
            name='USD/EGP',
            line=dict(color='#2ecc71', width=3),
            marker=dict(size=8)
        ))
    exchange_fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Exchange Rate (EGP per USD)",
        hovermode='x unified',
        template='plotly_white'
    )
    
    # Last update time
    from datetime import datetime
    last_update = f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    return gdp_fig, inflation_fig, exchange_fig, last_update


if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)
```

**Run the dashboard:**
```bash
python app.py
```

Open browser to: http://localhost:8050

You should see your dashboard with charts!

---

### PHASE 5: AUTOMATED UPDATES (3-4 hours)

#### Step 5.1: Create `scheduler.py`

```python
from apscheduler.schedulers.background import BackgroundScheduler
from data_fetcher import EconomicDataFetcher
from database import EconomicDatabase
from datetime import datetime

def update_economic_data():
    """Fetch fresh data and update database"""
    print(f"[{datetime.now()}] Starting scheduled data update...")
    
    fetcher = EconomicDataFetcher()
    db = EconomicDatabase()
    
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
        id='daily_update'
    )
    
    # Run once immediately on startup
    update_economic_data()
    
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
```

#### Step 5.2: Integrate Scheduler into `app.py`

Add these lines to the top of `app.py`:

```python
# Add after imports
from scheduler import start_scheduler

# Add before if __name__ == '__main__':
scheduler = start_scheduler()
```

---

### PHASE 6: PDF GENERATION (3-4 hours)

#### Step 6.1: Create `pdf_generator.py`

```python
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from datetime import datetime
import io
from database import EconomicDatabase
import plotly.graph_objs as go

def generate_pdf_report():
    """Generate PDF report with economic indicators"""
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=30,
        alignment=1  # Center
    )
    title = Paragraph("Egypt Economic Indicators Report", title_style)
    story.append(title)
    
    # Date
    date_style = ParagraphStyle(
        'DateStyle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#7f8c8d'),
        alignment=1
    )
    date_text = Paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y')}", date_style)
    story.append(date_text)
    story.append(Spacer(1, 0.5*inch))
    
    # Fetch data
    db = EconomicDatabase()
    gdp_df = db.get_all_gdp()
    inflation_df = db.get_all_inflation()
    exchange_df = db.get_all_exchange_rates()
    
    # Summary section
    summary_title = Paragraph("Summary", styles['Heading2'])
    story.append(summary_title)
    story.append(Spacer(1, 0.2*inch))
    
    if not gdp_df.empty:
        latest_gdp = gdp_df.iloc[-1]
        gdp_text = Paragraph(
            f"<b>Latest GDP:</b> ${latest_gdp['gdp_billions_usd']:.2f} billion (as of {latest_gdp['date'].strftime('%Y')})",
            styles['Normal']
        )
        story.append(gdp_text)
        story.append(Spacer(1, 0.1*inch))
    
    if not inflation_df.empty:
        latest_inflation = inflation_df.iloc[-1]
        inflation_text = Paragraph(
            f"<b>Latest Inflation Rate:</b> {latest_inflation['inflation_rate']:.2f}% (as of {latest_inflation['date'].strftime('%Y')})",
            styles['Normal']
        )
        story.append(inflation_text)
        story.append(Spacer(1, 0.1*inch))
    
    if not exchange_df.empty:
        latest_exchange = exchange_df.iloc[-1]
        exchange_text = Paragraph(
            f"<b>Latest Exchange Rate:</b> {latest_exchange['usd_egp_rate']:.2f} EGP per USD (as of {latest_exchange['date'].strftime('%Y-%m-%d')})",
            styles['Normal']
        )
        story.append(exchange_text)
        story.append(Spacer(1, 0.3*inch))
    
    # GDP Table
    if not gdp_df.empty:
        gdp_title = Paragraph("GDP Historical Data (Last 5 Years)", styles['Heading2'])
        story.append(gdp_title)
        story.append(Spacer(1, 0.2*inch))
        
        gdp_data = [['Year', 'GDP (Billions USD)']]
        for _, row in gdp_df.tail(5).iterrows():
            gdp_data.append([
                row['date'].strftime('%Y'),
                f"${row['gdp_billions_usd']:.2f}"
            ])
        
        gdp_table = Table(gdp_data)
        gdp_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(gdp_table)
        story.append(Spacer(1, 0.4*inch))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer


if __name__ == "__main__":
    # Test PDF generation
    pdf_buffer = generate_pdf_report()
    with open("test_report.pdf", "wb") as f:
        f.write(pdf_buffer.read())
    print("Test PDF generated: test_report.pdf")
```

#### Step 6.2: Add PDF Download to `app.py`

Add this callback to `app.py`:

```python
from flask import send_file
from pdf_generator import generate_pdf_report

@app.callback(
    Output('hidden-div', 'children'),
    Input('pdf-button', 'n_clicks')
)
def download_pdf(n_clicks):
    """Generate and download PDF report"""
    if n_clicks > 0:
        pdf_buffer = generate_pdf_report()
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'egypt_economic_report_{datetime.now().strftime("%Y%m%d")}.pdf'
        )
    return ''
```

---

### PHASE 7: DEPLOYMENT (4-5 hours)

#### Step 7.1: Prepare for Deployment

Create `Procfile` (for Heroku):
```
web: gunicorn app:server
```

Update `requirements.txt`:
```bash
pip install gunicorn
pip freeze > requirements.txt
```

Create `.gitignore`:
```
venv/
__pycache__/
*.pyc
.env
*.log
test_report.pdf
```

#### Step 7.2: Deploy to Heroku

```bash
# Install Heroku CLI: https://devcenter.heroku.com/articles/heroku-cli

# Login
heroku login

# Create app
heroku create egyptecon-dashboard

# Add PostgreSQL
heroku addons:create heroku-postgresql:mini

# Get database URL
heroku config

# Copy DATABASE_URL and update your .env for testing

# Push to Heroku
git init
git add .
git commit -m "Initial commit"
git push heroku main

# Open app
heroku open
```

**Alternative: Railway (Easier)**

1. Go to railway.app
2. Sign in with GitHub
3. "New Project" → "Deploy from GitHub repo"
4. Select your repo
5. Add PostgreSQL database (one click)
6. Add environment variable: `DATABASE_URL` (auto-populated)
7. Deploy!

---

## TESTING CHECKLIST

- [ ] Data fetcher returns data when run standalone
- [ ] Database tables created successfully
- [ ] Data inserted into database
- [ ] Dashboard displays charts at localhost:8050
- [ ] Refresh button updates data
- [ ] PDF download works
- [ ] Scheduler runs daily update
- [ ] Deployed app accessible at public URL
- [ ] No errors in Heroku/Railway logs

---

## TROUBLESHOOTING

**Problem:** APIs not returning data
- Check if API URLs changed
- Try different dates/parameters
- Use print statements to debug response

**Problem:** Database connection error
- Check DATABASE_URL in .env
- Verify PostgreSQL is running
- Check username/password

**Problem:** Dashboard not loading
- Check console for errors
- Verify all imports work
- Run `python app.py` and check terminal output

**Problem:** Deployment fails
- Check Procfile syntax
- Verify requirements.txt is complete
- Check Heroku logs: `heroku logs --tail`

---

## EXTENSIONS (Optional)

After core project works:

1. **Add more indicators**: Unemployment, Trade Balance
2. **Forecasting**: Use Prophet or ARIMA to predict trends
3. **Email alerts**: Send weekly reports via email
4. **User authentication**: Let users save custom views
5. **Compare countries**: Add comparison with other MENA countries

---

(Continued in next part...)
