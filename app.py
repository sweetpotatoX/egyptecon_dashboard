"""
Egypt Economic Dashboard
Main Dash application with interactive charts
"""

import dash
from dash import dcc, html, Input, Output
import plotly.graph_objs as go
from datetime import datetime
from database import EconomicDatabase
from scheduler import start_scheduler

# Initialize Dash app
app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}]
)
server = app.server  # For gunicorn deployment

# Initialize database
db = EconomicDatabase()

# Start background scheduler for daily updates
scheduler = start_scheduler()

# Color scheme
COLORS = {
    'primary': '#2c3e50',
    'secondary': '#7f8c8d',
    'gdp': '#3498db',
    'inflation': '#e74c3c',
    'exchange': '#2ecc71',
    'background': '#f8f9fa'
}

# App layout
app.layout = html.Div([
    # Header
    html.Div([
        html.H1("Egypt Economic Dashboard",
                style={'textAlign': 'center', 'color': COLORS['primary'], 'marginBottom': 5}),
        html.P("Real-time economic indicators for Egypt",
               style={'textAlign': 'center', 'color': COLORS['secondary'], 'fontSize': 18}),
    ], style={'padding': '20px', 'backgroundColor': COLORS['background']}),

    # Control buttons
    html.Div([
        html.Button('Refresh Data', id='refresh-button', n_clicks=0,
                    style={
                        'marginRight': 20,
                        'padding': '10px 25px',
                        'fontSize': 16,
                        'backgroundColor': COLORS['primary'],
                        'color': 'white',
                        'border': 'none',
                        'borderRadius': '5px',
                        'cursor': 'pointer'
                    }),
        html.A(
            html.Button('Download PDF Report',
                        style={
                            'padding': '10px 25px',
                            'fontSize': 16,
                            'backgroundColor': COLORS['gdp'],
                            'color': 'white',
                            'border': 'none',
                            'borderRadius': '5px',
                            'cursor': 'pointer'
                        }),
            href='/download-pdf',
            id='pdf-link'
        ),
        html.Div(id='last-update', style={'marginTop': 15, 'fontStyle': 'italic', 'color': COLORS['secondary']})
    ], style={'textAlign': 'center', 'marginBottom': 30, 'padding': '10px'}),

    # Summary cards
    html.Div([
        html.Div([
            html.H4("Latest GDP", style={'color': COLORS['secondary'], 'marginBottom': 5}),
            html.H2(id='gdp-value', style={'color': COLORS['gdp'], 'margin': 0}),
        ], style={'flex': 1, 'textAlign': 'center', 'padding': '20px', 'backgroundColor': 'white',
                  'borderRadius': '10px', 'margin': '0 10px', 'boxShadow': '0 2px 5px rgba(0,0,0,0.1)'}),
        html.Div([
            html.H4("Latest Inflation", style={'color': COLORS['secondary'], 'marginBottom': 5}),
            html.H2(id='inflation-value', style={'color': COLORS['inflation'], 'margin': 0}),
        ], style={'flex': 1, 'textAlign': 'center', 'padding': '20px', 'backgroundColor': 'white',
                  'borderRadius': '10px', 'margin': '0 10px', 'boxShadow': '0 2px 5px rgba(0,0,0,0.1)'}),
        html.Div([
            html.H4("USD/EGP Rate", style={'color': COLORS['secondary'], 'marginBottom': 5}),
            html.H2(id='exchange-value', style={'color': COLORS['exchange'], 'margin': 0}),
        ], style={'flex': 1, 'textAlign': 'center', 'padding': '20px', 'backgroundColor': 'white',
                  'borderRadius': '10px', 'margin': '0 10px', 'boxShadow': '0 2px 5px rgba(0,0,0,0.1)'}),
    ], style={'display': 'flex', 'justifyContent': 'center', 'marginBottom': 40, 'padding': '0 20px'}),

    # GDP Chart
    html.Div([
        html.H3("GDP (Billions USD)", style={'color': COLORS['primary'], 'marginLeft': 20}),
        dcc.Graph(id='gdp-chart', config={'displayModeBar': True, 'scrollZoom': True})
    ], style={'marginBottom': 40, 'backgroundColor': 'white', 'borderRadius': '10px',
              'padding': '20px', 'margin': '0 20px 40px 20px', 'boxShadow': '0 2px 5px rgba(0,0,0,0.1)'}),

    # Inflation Chart
    html.Div([
        html.H3("Inflation Rate (%)", style={'color': COLORS['primary'], 'marginLeft': 20}),
        dcc.Graph(id='inflation-chart', config={'displayModeBar': True, 'scrollZoom': True})
    ], style={'marginBottom': 40, 'backgroundColor': 'white', 'borderRadius': '10px',
              'padding': '20px', 'margin': '0 20px 40px 20px', 'boxShadow': '0 2px 5px rgba(0,0,0,0.1)'}),

    # Exchange Rate Chart
    html.Div([
        html.H3("USD/EGP Exchange Rate", style={'color': COLORS['primary'], 'marginLeft': 20}),
        dcc.Graph(id='exchange-chart', config={'displayModeBar': True, 'scrollZoom': True})
    ], style={'marginBottom': 40, 'backgroundColor': 'white', 'borderRadius': '10px',
              'padding': '20px', 'margin': '0 20px 40px 20px', 'boxShadow': '0 2px 5px rgba(0,0,0,0.1)'}),

    # Footer
    html.Div([
        html.P("Data sources: World Bank API, Exchange Rate API",
               style={'textAlign': 'center', 'color': COLORS['secondary'], 'fontSize': 14}),
        html.P("Built by Abdelrahman Bahaa",
               style={'textAlign': 'center', 'color': COLORS['secondary'], 'fontSize': 14}),
    ], style={'padding': '20px', 'backgroundColor': COLORS['background']}),

    # Interval component for auto-refresh (every 1 minute)
    dcc.Interval(id='interval-component', interval=60000, n_intervals=0),

], style={'fontFamily': 'Arial, sans-serif', 'backgroundColor': COLORS['background'], 'minHeight': '100vh'})


@app.callback(
    [Output('gdp-chart', 'figure'),
     Output('inflation-chart', 'figure'),
     Output('exchange-chart', 'figure'),
     Output('last-update', 'children'),
     Output('gdp-value', 'children'),
     Output('inflation-value', 'children'),
     Output('exchange-value', 'children')],
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
            line=dict(color=COLORS['gdp'], width=3),
            marker=dict(size=8),
            hovertemplate='Year: %{x|%Y}<br>GDP: $%{y:.2f}B<extra></extra>'
        ))
    gdp_fig.update_layout(
        xaxis_title="Year",
        yaxis_title="GDP (Billions USD)",
        hovermode='x unified',
        template='plotly_white',
        margin=dict(l=50, r=30, t=30, b=50)
    )

    # Inflation Chart
    inflation_fig = go.Figure()
    if not inflation_df.empty:
        inflation_fig.add_trace(go.Scatter(
            x=inflation_df['date'],
            y=inflation_df['inflation_rate'],
            mode='lines+markers',
            name='Inflation Rate',
            line=dict(color=COLORS['inflation'], width=3),
            marker=dict(size=8),
            hovertemplate='Year: %{x|%Y}<br>Inflation: %{y:.2f}%<extra></extra>'
        ))
    inflation_fig.update_layout(
        xaxis_title="Year",
        yaxis_title="Inflation Rate (%)",
        hovermode='x unified',
        template='plotly_white',
        margin=dict(l=50, r=30, t=30, b=50)
    )

    # Exchange Rate Chart
    exchange_fig = go.Figure()
    if not exchange_df.empty:
        exchange_fig.add_trace(go.Scatter(
            x=exchange_df['date'],
            y=exchange_df['usd_egp_rate'],
            mode='lines+markers',
            name='USD/EGP',
            line=dict(color=COLORS['exchange'], width=3),
            marker=dict(size=8),
            hovertemplate='Date: %{x|%Y-%m-%d %H:%M}<br>Rate: %{y:.2f} EGP<extra></extra>'
        ))
    exchange_fig.update_layout(
        xaxis_title="Date/Time",
        yaxis_title="Exchange Rate (EGP per USD)",
        hovermode='x unified',
        template='plotly_white',
        margin=dict(l=50, r=30, t=30, b=50)
    )

    # Last update time
    last_update = f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    # Summary values
    gdp_value = f"${gdp_df.iloc[-1]['gdp_billions_usd']:.2f}B" if not gdp_df.empty else "N/A"
    inflation_value = f"{inflation_df.iloc[-1]['inflation_rate']:.2f}%" if not inflation_df.empty else "N/A"
    exchange_value = f"{exchange_df.iloc[-1]['usd_egp_rate']:.2f} EGP" if not exchange_df.empty else "N/A"

    return gdp_fig, inflation_fig, exchange_fig, last_update, gdp_value, inflation_value, exchange_value


# PDF download route
@server.route('/download-pdf')
def download_pdf():
    """Generate and download PDF report"""
    from flask import send_file
    from pdf_generator import generate_pdf_report

    pdf_buffer = generate_pdf_report()
    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'egypt_economic_report_{datetime.now().strftime("%Y%m%d")}.pdf'
    )


if __name__ == '__main__':
    # Initialize database tables
    db.create_tables()

    # Run the app
    app.run_server(debug=True, host='0.0.0.0', port=8050)
