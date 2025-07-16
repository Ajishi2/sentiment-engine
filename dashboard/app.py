"""
Real-time dashboard for the Fear & Greed Sentiment Engine
"""
import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import asyncio
import threading
from datetime import datetime, timedelta
import json
import numpy as np

from main import SentimentEngine
from core.data_models import TradingSignal, SignalType

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Fear & Greed Sentiment Engine"

# Global variables for data storage
sentiment_data = []
signal_data = []
fear_greed_data = []
system_status = {}
engine = None

def create_layout():
    """Create the dashboard layout"""
    return dbc.Container([
        # Header
        dbc.Row([
            dbc.Col([
                html.H1("Fear & Greed Sentiment Engine", className="text-center mb-4"),
                html.P("Real-time sentiment analysis and trading signal generation", 
                      className="text-center text-muted")
            ])
        ]),
        
        # Status Row
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("System Status", className="card-title"),
                        html.Div(id="system-status", children="Initializing...")
                    ])
                ], color="primary", outline=True)
            ], width=12)
        ], className="mb-4"),
        
        # Main Dashboard Row
        dbc.Row([
            # Fear & Greed Index
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("Fear & Greed Index", className="card-title"),
                        dcc.Graph(id="fear-greed-gauge")
                    ])
                ])
            ], width=6),
            
            # Latest Signals
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("Latest Signals", className="card-title"),
                        html.Div(id="latest-signals")
                    ])
                ])
            ], width=6)
        ], className="mb-4"),
        
        # Charts Row
        dbc.Row([
            # Sentiment Over Time
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("Sentiment Analysis", className="card-title"),
                        dcc.Graph(id="sentiment-timeline")
                    ])
                ])
            ], width=12)
        ], className="mb-4"),
        
        # Performance Row
        dbc.Row([
            # Signal Performance
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("Signal Performance", className="card-title"),
                        dcc.Graph(id="signal-performance")
                    ])
                ])
            ], width=6),
            
            # Asset Breakdown
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("Asset Sentiment", className="card-title"),
                        dcc.Graph(id="asset-breakdown")
                    ])
                ])
            ], width=6)
        ]),
        
        # Auto-refresh interval
        dcc.Interval(
            id='interval-component',
            interval=5*1000,  # Update every 5 seconds
            n_intervals=0
        )
    ], fluid=True)

app.layout = create_layout()

@app.callback(
    Output('system-status', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_system_status(n):
    """Update system status display"""
    if not system_status:
        return dbc.Alert("System initializing...", color="warning")
    
    status_items = [
        dbc.ListGroupItem([
            html.Strong("Engine Status: "),
            dbc.Badge("Running" if system_status.get('is_running', False) else "Stopped", 
                     color="success" if system_status.get('is_running', False) else "danger")
        ]),
        dbc.ListGroupItem([
            html.Strong("Signals Generated: "),
            str(system_status.get('total_signals_generated', 0))
        ]),
        dbc.ListGroupItem([
            html.Strong("Data Sources Active: "),
            str(system_status.get('data_sources_active', 0))
        ]),
        dbc.ListGroupItem([
            html.Strong("Last Signal: "),
            str(system_status.get('last_signal_time', 'None'))[:19] if system_status.get('last_signal_time') else 'None'
        ])
    ]
    
    return dbc.ListGroup(status_items, flush=True)

@app.callback(
    Output('fear-greed-gauge', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_fear_greed_gauge(n):
    """Update Fear & Greed Index gauge"""
    if not fear_greed_data:
        # Default gauge
        current_value = 50
        classification = "Neutral"
    else:
        latest = fear_greed_data[-1]
        current_value = latest.get('overall_score', 50)
        classification = latest.get('classification', 'Neutral')
    
    # Create gauge chart
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = current_value,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': f"Fear & Greed Index<br><span style='font-size:0.8em;color:gray'>{classification}</span>"},
        delta = {'reference': 50},
        gauge = {
            'axis': {'range': [None, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 25], 'color': "red"},
                {'range': [25, 45], 'color': "orange"},
                {'range': [45, 55], 'color': "yellow"},
                {'range': [55, 75], 'color': "lightgreen"},
                {'range': [75, 100], 'color': "green"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    
    fig.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20))
    return fig

@app.callback(
    Output('latest-signals', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_latest_signals(n):
    """Update latest signals display"""
    if not signal_data:
        return dbc.Alert("No signals generated yet", color="info")
    
    # Get last 5 signals
    recent_signals = signal_data[-5:]
    
    signal_items = []
    for signal in recent_signals:
        # Determine color based on signal type
        if signal.get('signal_type') == 'BUY':
            color = "success"
            icon = "↗"
        elif signal.get('signal_type') == 'SELL':
            color = "danger"
            icon = "↘"
        else:
            color = "secondary"
            icon = "→"
        
        signal_items.append(
            dbc.ListGroupItem([
                dbc.Row([
                    dbc.Col([
                        html.Strong(f"{icon} {signal.get('asset', 'Unknown')}", className=f"text-{color}"),
                        html.Br(),
                        html.Small(f"Confidence: {signal.get('confidence', 0):.2f}")
                    ], width=4),
                    dbc.Col([
                        html.Small(signal.get('reasoning', 'No reasoning provided')[:100] + "...")
                    ], width=8)
                ])
            ])
        )
    
    return dbc.ListGroup(signal_items, flush=True)

@app.callback(
    Output('sentiment-timeline', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_sentiment_timeline(n):
    """Update sentiment timeline chart"""
    if not sentiment_data:
        # Create empty chart
        fig = go.Figure()
        fig.add_annotation(text="No sentiment data available", 
                          xref="paper", yref="paper", x=0.5, y=0.5)
        fig.update_layout(height=400, title="Sentiment Over Time")
        return fig
    
    # Create sample sentiment timeline
    timestamps = [datetime.now() - timedelta(minutes=i) for i in range(60, 0, -1)]
    sentiment_scores = np.random.normal(0, 0.3, 60)  # Mock data
    
    df = pd.DataFrame({
        'timestamp': timestamps,
        'sentiment': sentiment_scores
    })
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['timestamp'],
        y=df['sentiment'],
        mode='lines+markers',
        name='Sentiment Score',
        line=dict(color='blue', width=2),
        marker=dict(size=4)
    ))
    
    # Add horizontal lines for thresholds
    fig.add_hline(y=0.3, line_dash="dash", line_color="green", annotation_text="Bullish")
    fig.add_hline(y=-0.3, line_dash="dash", line_color="red", annotation_text="Bearish")
    fig.add_hline(y=0, line_dash="dash", line_color="gray", annotation_text="Neutral")
    
    fig.update_layout(
        title="Market Sentiment Over Time",
        xaxis_title="Time",
        yaxis_title="Sentiment Score",
        height=400,
        showlegend=True
    )
    
    return fig

@app.callback(
    Output('signal-performance', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_signal_performance(n):
    """Update signal performance chart"""
    if not signal_data:
        fig = go.Figure()
        fig.add_annotation(text="No signal data available", 
                          xref="paper", yref="paper", x=0.5, y=0.5)
        fig.update_layout(height=300, title="Signal Performance")
        return fig
    
    # Mock performance data
    performance_data = {
        'BUY': {'count': 15, 'avg_return': 0.05},
        'SELL': {'count': 8, 'avg_return': 0.03},
        'HOLD': {'count': 22, 'avg_return': 0.01}
    }
    
    signals = list(performance_data.keys())
    counts = [performance_data[s]['count'] for s in signals]
    returns = [performance_data[s]['avg_return'] * 100 for s in signals]
    
    fig = go.Figure()
    
    # Bar chart for signal counts
    fig.add_trace(go.Bar(
        x=signals,
        y=counts,
        name='Signal Count',
        yaxis='y',
        marker_color=['green', 'red', 'blue']
    ))
    
    # Line chart for average returns
    fig.add_trace(go.Scatter(
        x=signals,
        y=returns,
        mode='lines+markers',
        name='Avg Return (%)',
        yaxis='y2',
        line=dict(color='orange', width=3),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        title="Signal Performance Overview",
        xaxis_title="Signal Type",
        yaxis=dict(title="Count", side="left"),
        yaxis2=dict(title="Average Return (%)", side="right", overlaying="y"),
        height=300,
        showlegend=True
    )
    
    return fig

@app.callback(
    Output('asset-breakdown', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_asset_breakdown(n):
    """Update asset sentiment breakdown"""
    # Mock asset sentiment data
    assets = ['BTC', 'ETH', 'AAPL', 'TSLA', 'MARKET']
    sentiment_scores = np.random.uniform(-0.5, 0.5, len(assets))
    
    colors = ['red' if s < -0.2 else 'orange' if s < 0.2 else 'green' for s in sentiment_scores]
    
    fig = go.Figure(go.Bar(
        x=assets,
        y=sentiment_scores,
        marker_color=colors,
        text=[f'{s:.2f}' for s in sentiment_scores],
        textposition='auto'
    ))
    
    fig.update_layout(
        title="Current Asset Sentiment",
        xaxis_title="Asset",
        yaxis_title="Sentiment Score",
        height=300,
        showlegend=False
    )
    
    # Add threshold lines
    fig.add_hline(y=0.2, line_dash="dash", line_color="green", annotation_text="Bullish")
    fig.add_hline(y=-0.2, line_dash="dash", line_color="red", annotation_text="Bearish")
    
    return fig

def run_engine_background():
    """Run the sentiment engine in background"""
    global engine, system_status, signal_data, fear_greed_data
    
    async def engine_runner():
        global engine
        engine = SentimentEngine()
        
        # Start the engine
        engine_task = asyncio.create_task(engine.start())
        
        # Update data periodically
        while True:
            try:
                # Update system status
                status = await engine.get_system_status()
                system_status.update(status)
                
                # Get latest signals
                latest_signals = await engine.get_latest_signals(20)
                signal_data.clear()
                for signal in latest_signals:
                    signal_data.append({
                        'asset': signal.asset,
                        'signal_type': signal.signal_type.value,
                        'confidence': signal.confidence,
                        'strength': signal.strength,
                        'reasoning': signal.reasoning,
                        'timestamp': signal.timestamp
                    })
                
                # Mock fear & greed data
                fear_greed_data.append({
                    'overall_score': np.random.uniform(20, 80),
                    'classification': np.random.choice(['Fear', 'Neutral', 'Greed']),
                    'timestamp': datetime.now()
                })
                
                # Keep only recent data
                if len(fear_greed_data) > 100:
                    fear_greed_data.pop(0)
                
                await asyncio.sleep(10)  # Update every 10 seconds
                
            except Exception as e:
                print(f"Error in background engine: {e}")
                await asyncio.sleep(5)
    
    # Run the async function
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(engine_runner())

if __name__ == '__main__':
    # Start background engine
    engine_thread = threading.Thread(target=run_engine_background, daemon=True)
    engine_thread.start()
    
    # Start dashboard
    print("Starting Fear & Greed Sentiment Engine Dashboard...")
    print("Dashboard will be available at: http://localhost:8050")
    app.run_server(debug=False, host='0.0.0.0', port=8050)