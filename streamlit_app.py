# streamlit_app.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time
from typing import Dict, Any, Optional
import json
import warnings

# Import Warren AI modules
try:
    from main import WarrenAI
    from core.config import Config
    from models.stock import (
        TrendDirection, RSISignal, Recommendation,
        StockMetadata, FundamentalMetrics, TechnicalIndicators
    )
    from utils.formatter import Formatter
    import yfinance as yf
except ImportError as e:
    st.error(f"Error importing modules: {str(e)}")
    st.info("Please ensure all modules are properly installed")

warnings.filterwarnings('ignore')

# ============================================
# PAGE CONFIGURATION
# ============================================

st.set_page_config(
    page_title="Warren AI - Advanced Stock Analysis",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/yourusername/warren-ai',
        'Report a bug': 'https://github.com/yourusername/warren-ai/issues',
        'About': """
        # Warren AI v2.0
        
        Advanced Stock Analysis Platform dengan:
        - Analisis Fundamental & Teknikal
        - Portfolio Tracking
        - AI Recommendations
        - Real-time Market Data
        """
    }
)

# ============================================
# CUSTOM CSS STYLING
# ============================================

def load_custom_css():
    """Load custom CSS styling"""
    st.markdown("""
    <style>
    /* Main styling */
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
    
    .sub-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #4a5568;
        margin-bottom: 1rem;
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border: 1px solid #e2e8f0;
        transition: transform 0.2s;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #2d3748;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #718096;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .positive-change {
        color: #38a169;
    }
    
    .negative-change {
        color: #e53e3e;
    }
    
    .neutral-change {
        color: #718096;
    }
    
    .trend-bullish {
        background: linear-gradient(90deg, #c6f6d5 0%, #9ae6b4 100%);
        padding: 0.5rem;
        border-radius: 5px;
        font-weight: 600;
    }
    
    .trend-bearish {
        background: linear-gradient(90deg, #fed7d7 0%, #fc8181 100%);
        padding: 0.5rem;
        border-radius: 5px;
        font-weight: 600;
    }
    
    .trend-sideways {
        background: linear-gradient(90deg, #e2e8f0 0%, #cbd5e0 100%);
        padding: 0.5rem;
        border-radius: 5px;
        font-weight: 600;
    }
    
    .recommendation-strong-buy {
        background: linear-gradient(90deg, #48bb78 0%, #38a169 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 700;
        text-align: center;
    }
    
    .recommendation-buy {
        background: linear-gradient(90deg, #68d391 0%, #48bb78 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 700;
        text-align: center;
    }
    
    .recommendation-hold {
        background: linear-gradient(90deg, #ecc94b 0%, #d69e2e 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 700;
        text-align: center;
    }
    
    .recommendation-sell {
        background: linear-gradient(90deg, #fc8181 0%, #f56565 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 700;
        text-align: center;
    }
    
    .recommendation-strong-sell {
        background: linear-gradient(90deg, #e53e3e 0%, #c53030 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 700;
        text-align: center;
    }
    
    .stock-card {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        border: 1px solid #e2e8f0;
        transition: all 0.3s ease;
    }
    
    .stock-card:hover {
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
        transform: translateY(-2px);
    }
    
    /* Custom tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f7fafc;
        border-radius: 5px 5px 0 0;
        gap: 1px;
        padding: 10px 20px;
    }
    
    /* Sidebar styling */
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f7fafc 0%, #edf2f7 100%);
    }
    
    /* Loading animation */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    .pulse {
        animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }
    </style>
    """, unsafe_allow_html=True)

# ============================================
# INITIALIZATION
# ============================================

@st.cache_resource
def initialize_warren_ai():
    """Initialize Warren AI with caching"""
    config = Config(
        data_provider='yahoo',
        default_period='1y',
        cache_enabled=True,
        cache_duration=3600
    )
    
    try:
        app = WarrenAI(config)
        return app
    except Exception as e:
        st.error(f"Failed to initialize Warren AI: {str(e)}")
        return None

@st.cache_resource
def get_formatter():
    """Initialize formatter"""
    return Formatter()

def initialize_session_state():
    """Initialize session state variables"""
    if 'analysis_history' not in st.session_state:
        st.session_state.analysis_history = []
    
    if 'portfolio' not in st.session_state:
        st.session_state.portfolio = {}
    
    if 'watchlist' not in st.session_state:
        st.session_state.watchlist = ['BBCA.JK', 'BBRI.JK', 'BMRI.JK', 'TLKM.JK']
    
    if 'selected_ticker' not in st.session_state:
        st.session_state.selected_ticker = 'BBCA.JK'
    
    if 'analysis_result' not in st.session_state:
        st.session_state.analysis_result = None

# ============================================
# VISUALIZATION FUNCTIONS
# ============================================

def create_price_chart(price_data, ticker):
    """Create interactive price chart with Plotly"""
    
    if not price_data or len(price_data) < 2:
        return go.Figure()
    
    # Convert to DataFrame
    df = pd.DataFrame([{
        'date': p.date,
        'open': p.open,
        'high': p.high,
        'low': p.low,
        'close': p.close,
        'volume': p.volume
    } for p in price_data])
    
    df.set_index('date', inplace=True)
    
    # Create candlestick chart
    fig = go.Figure(data=[
        go.Candlestick(
            x=df.index,
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name='Price',
            increasing_line_color='#38a169',
            decreasing_line_color='#e53e3e'
        )
    ])
    
    # Add volume as bar chart (secondary y-axis)
    fig.add_trace(go.Bar(
        x=df.index,
        y=df['volume'],
        name='Volume',
        yaxis='y2',
        marker_color='#a0aec0',
        opacity=0.3
    ))
    
    # Layout configuration
    fig.update_layout(
        title=f'{ticker} - Price & Volume Chart',
        yaxis_title='Price',
        yaxis2=dict(
            title='Volume',
            overlaying='y',
            side='right',
            showgrid=False
        ),
        xaxis_title='Date',
        template='plotly_white',
        hovermode='x unified',
        height=500,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    # Add range slider
    fig.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1M", step="month", stepmode="backward"),
                dict(count=3, label="3M", step="month", stepmode="backward"),
                dict(count=6, label="6M", step="month", stepmode="backward"),
                dict(count=1, label="1Y", step="year", stepmode="backward"),
                dict(step="all")
            ])
        )
    )
    
    return fig

def create_technical_indicators_chart(price_data, indicators):
    """Create chart with technical indicators"""
    
    if not price_data:
        return go.Figure()
    
    # Convert to DataFrame
    df = pd.DataFrame([{
        'date': p.date,
        'close': p.close,
        'volume': p.volume
    } for p in price_data])
    
    df.set_index('date', inplace=True)
    
    # Create subplot figure
    fig = go.Figure()
    
    # Add price line
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['close'],
        name='Price',
        line=dict(color='#4299e1', width=2)
    ))
    
    # Add moving averages if available
    if indicators and hasattr(indicators, 'ma_20') and indicators.ma_20:
        # Calculate MAs from data for chart
        df['MA20'] = df['close'].rolling(20).mean()
        df['MA50'] = df['close'].rolling(50).mean()
        df['MA200'] = df['close'].rolling(200).mean()
        
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['MA20'],
            name='MA20',
            line=dict(color='#ecc94b', width=1, dash='dash')
        ))
        
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['MA50'],
            name='MA50',
            line=dict(color='#ed8936', width=1, dash='dash')
        ))
        
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['MA200'],
            name='MA200',
            line=dict(color='#9f7aea', width=2)
        ))
    
    # Layout
    fig.update_layout(
        title='Technical Indicators',
        yaxis_title='Price',
        template='plotly_white',
        height=400,
        hovermode='x unified'
    )
    
    return fig

def create_rsi_chart(price_data):
    """Create RSI chart"""
    
    if not price_data or len(price_data) < 15:
        return go.Figure()
    
    df = pd.DataFrame([{
        'date': p.date,
        'close': p.close
    } for p in price_data])
    
    df.set_index('date', inplace=True)
    
    # Calculate RSI
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    fig = go.Figure()
    
    # Add RSI line
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['RSI'],
        name='RSI',
        line=dict(color='#9f7aea', width=2)
    ))
    
    # Add overbought/oversold lines
    fig.add_hline(y=70, line_dash="dash", line_color="#e53e3e", annotation_text="Overbought")
    fig.add_hline(y=30, line_dash="dash", line_color="#38a169", annotation_text="Oversold")
    fig.add_hline(y=50, line_dash="dot", line_color="#a0aec0")
    
    fig.update_layout(
        title='RSI (14)',
        yaxis_title='RSI',
        yaxis_range=[0, 100],
        template='plotly_white',
        height=300
    )
    
    return fig

def create_macd_chart(price_data):
    """Create MACD chart"""
    
    if not price_data or len(price_data) < 35:
        return go.Figure()
    
    df = pd.DataFrame([{'date': p.date, 'close': p.close} for p in price_data])
    df.set_index('date', inplace=True)
    
    # Calculate MACD
    exp12 = df['close'].ewm(span=12, adjust=False).mean()
    exp26 = df['close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = exp12 - exp26
    df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['Histogram'] = df['MACD'] - df['Signal']
    
    fig = go.Figure()
    
    # Add MACD line
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['MACD'],
        name='MACD',
        line=dict(color='#4299e1', width=2)
    ))
    
    # Add Signal line
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['Signal'],
        name='Signal',
        line=dict(color='#ed8936', width=2)
    ))
    
    # Add Histogram
    colors = ['#38a169' if val >= 0 else '#e53e3e' for val in df['Histogram']]
    fig.add_trace(go.Bar(
        x=df.index,
        y=df['Histogram'],
        name='Histogram',
        marker_color=colors,
        opacity=0.5
    ))
    
    fig.update_layout(
        title='MACD',
        yaxis_title='MACD',
        template='plotly_white',
        height=300
    )
    
    return fig

def create_fundamental_radar_chart(fundamental_data):
    """Create radar chart for fundamental metrics"""
    
    if not fundamental_data:
        return go.Figure()
    
    categories = ['Valuation', 'Profitability', 'Growth', 'Financial Health', 'Dividend']
    
    # Normalize values (this is simplified)
    values = [0.7, 0.8, 0.6, 0.9, 0.5]  # Example values
    
    fig = go.Figure(data=go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        line_color='#4299e1',
        fillcolor='rgba(66, 153, 225, 0.3)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )
        ),
        showlegend=False,
        title='Fundamental Score Radar',
        height=400
    )
    
    return fig

def create_recommendation_gauge(score, max_score=10):
    """Create gauge chart for recommendation score"""
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Investment Score", 'font': {'size': 24}},
        gauge={
            'axis': {'range': [0, max_score], 'tickwidth': 1},
            'bar': {'color': "#4299e1"},
            'steps': [
                {'range': [0, 4], 'color': "#e53e3e"},
                {'range': [4, 7], 'color': "#ecc94b"},
                {'range': [7, max_score], 'color': "#38a169"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': score
            }
        }
    ))
    
    fig.update_layout(height=300)
    return fig

# ============================================
# UI COMPONENTS
# ============================================

def render_metric_card(label, value, change=None, change_label=None, icon=None):
    """Render a metric card"""
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(f'<div class="metric-label">{label}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{value}</div>', unsafe_allow_html=True)
    
    if change is not None and change_label:
        change_class = "positive-change" if change > 0 else "negative-change" if change < 0 else "neutral-change"
        with col2:
            st.markdown(f'<div style="text-align: right;">', unsafe_allow_html=True)
            if icon:
                st.markdown(f'<div>{icon}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="{change_class}">{change_label}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

def render_trend_indicator(trend):
    """Render trend indicator"""
    
    trend_map = {
        'strong_bullish': ('🟢🟢 BULLISH KUAT', 'trend-bullish'),
        'bullish': ('🟢 BULLISH', 'trend-bullish'),
        'sideways': ('⚪ SIDEWAYS', 'trend-sideways'),
        'bearish': ('🔴 BEARISH', 'trend-bearish'),
        'strong_bearish': ('🔴🔴 BEARISH KUAT', 'trend-bearish')
    }
    
    text, css_class = trend_map.get(trend, ('N/A', ''))
    st.markdown(f'<div class="{css_class}">{text}</div>', unsafe_allow_html=True)

def render_recommendation_badge(recommendation):
    """Render recommendation badge"""
    
    rec_map = {
        'strong_buy': ('🎯 STRONG BUY', 'recommendation-strong-buy'),
        'buy': ('✅ BUY', 'recommendation-buy'),
        'hold': ('⏸️ HOLD', 'recommendation-hold'),
        'sell': ('🔻 SELL', 'recommendation-sell'),
        'strong_sell': ('❌ STRONG SELL', 'recommendation-strong-sell')
    }
    
    text, css_class = rec_map.get(recommendation, ('N/A', ''))
    st.markdown(f'<div class="{css_class}">{text}</div>', unsafe_allow_html=True)

def render_stock_card(ticker, name, price, change, recommendation):
    """Render stock card for watchlist"""
    
    st.markdown(f"""
    <div class="stock-card">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h4 style="margin: 0; color: #2d3748;">{name}</h4>
                <p style="margin: 0; color: #718096; font-size: 0.9rem;">{ticker}</p>
            </div>
            <div style="text-align: right;">
                <h3 style="margin: 0; color: #2d3748;">{price}</h3>
                <p style="margin: 0; color: {'#38a169' if change >= 0 else '#e53e3e'}">
                    {'+' if change >= 0 else ''}{change:.2f}%
                </p>
            </div>
        </div>
        <div style="margin-top: 10px;">
            {render_recommendation_badge_html(recommendation)}
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_recommendation_badge_html(recommendation):
    """Render recommendation badge as HTML"""
    
    rec_map = {
        'strong_buy': ('🎯 STRONG BUY', '#38a169'),
        'buy': ('✅ BUY', '#48bb78'),
        'hold': ('⏸️ HOLD', '#ecc94b'),
        'sell': ('🔻 SELL', '#f56565'),
        'strong_sell': ('❌ STRONG SELL', '#e53e3e')
    }
    
    text, color = rec_map.get(recommendation, ('N/A', '#718096'))
    
    return f"""
    <span style="
        background-color: {color};
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    ">
        {text}
    </span>
    """

# ============================================
# SIDEBAR
# ============================================

def render_sidebar():
    """Render sidebar with navigation and controls"""
    
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0;">
            <h1 style="margin: 0; color: #4299e1;">📈</h1>
            <h2 style="margin: 0; color: #2d3748;">Warren AI</h2>
            <p style="margin: 0; color: #718096; font-size: 0.9rem;">Advanced Stock Analysis</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # Navigation
        st.markdown("### 🧭 Navigation")
        nav_options = ["📊 Dashboard", "🔍 Stock Analysis", "💰 Portfolio", "📈 Market Overview", "⚙️ Settings"]
        selected_nav = st.radio("", nav_options, label_visibility="collapsed")
        
        st.divider()
        
        # Stock Search
        st.markdown("### 🔍 Stock Search")
        
        search_col1, search_col2 = st.columns([3, 1])
        with search_col1:
            ticker_input = st.text_input(
                "Enter ticker:",
                value=st.session_state.selected_ticker,
                placeholder="e.g., BBCA.JK, BBRI",
                label_visibility="collapsed"
            )
        
        with search_col2:
            analyze_button = st.button("Analyze", type="primary", use_container_width=True)
        
        if analyze_button and ticker_input:
            st.session_state.selected_ticker = ticker_input.upper()
            st.rerun()
        
        # Popular tickers
        st.markdown("#### Popular Stocks")
        popular_cols = st.columns(2)
        popular_stocks = [
            ("BBCA", "Bank Central Asia"),
            ("BBRI", "Bank Rakyat Indonesia"),
            ("BMRI", "Bank Mandiri"),
            ("TLKM", "Telkom Indonesia"),
            ("ASII", "Astra International"),
            ("UNVR", "Unilever Indonesia")
        ]
        
        for idx, (ticker, name) in enumerate(popular_stocks):
            col = popular_cols[idx % 2]
            if col.button(f"{ticker}: {name}", use_container_width=True):
                st.session_state.selected_ticker = f"{ticker}.JK"
                st.rerun()
        
        st.divider()
        
        # Watchlist
        st.markdown("### ⭐ Watchlist")
        if st.session_state.watchlist:
            for ticker in st.session_state.watchlist[:5]:  # Show first 5
                if st.button(f"📊 {ticker}", key=f"watch_{ticker}", use_container_width=True):
                    st.session_state.selected_ticker = ticker
                    st.rerun()
        else:
            st.info("Add stocks to your watchlist")
        
        # Add to watchlist
        if ticker_input and ticker_input not in st.session_state.watchlist:
            if st.button("➕ Add to Watchlist", use_container_width=True):
                st.session_state.watchlist.append(ticker_input.upper())
                st.success(f"Added {ticker_input} to watchlist")
                st.rerun()
        
        st.divider()
        
        # Settings
        with st.expander("⚙️ Settings"):
            analysis_period = st.selectbox(
                "Analysis Period",
                ["3mo", "6mo", "1y", "2y", "5y"],
                index=2
            )
            
            auto_refresh = st.checkbox("Auto-refresh data", value=False)
            if auto_refresh:
                refresh_interval = st.slider("Refresh interval (minutes)", 1, 60, 5)
        
        st.divider()
        
        # Footer
        st.markdown("""
        <div style="text-align: center; color: #718096; font-size: 0.8rem; padding: 1rem 0;">
            <p>Warren AI v2.0</p>
            <p>Data provided by Yahoo Finance</p>
            <p>© 2024 Warren AI. All rights reserved.</p>
        </div>
        """, unsafe_allow_html=True)
    
    return selected_nav

# ============================================
# MAIN PAGES
# ============================================

def render_dashboard():
    """Render main dashboard page"""
    
    st.markdown('<div class="main-header">📊 Warren AI Dashboard</div>', unsafe_allow_html=True)
    
    # Quick stats row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        render_metric_card("Market Cap", "Rp 8,500 T", 2.5, "+2.5%", "📈")
    
    with col2:
        render_metric_card("JCI Index", "7,215.45", 15.32, "+0.21%", "📊")
    
    with col3:
        render_metric_card("Volume", "25.4B", -3.2, "-3.2%", "💹")
    
    with col4:
        render_metric_card("Advancers", "245", None, None, "✅")
    
    st.divider()
    
    # Market overview and analysis
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="sub-header">📈 Market Overview</div>', unsafe_allow_html=True)
        
        # Sample market chart
        dates = pd.date_range(start='2024-01-01', end='2024-12-01', freq='D')
        market_data = pd.DataFrame({
            'Date': dates,
            'Index': np.random.randn(len(dates)).cumsum() + 7000
        })
        
        fig = px.line(market_data, x='Date', y='Index', title='Jakarta Composite Index (JCI)')
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown('<div class="sub-header">🔥 Top Gainers</div>', unsafe_allow_html=True)
        
        # Sample top gainers
        gainers = [
            {"ticker": "BBCA.JK", "name": "Bank BCA", "change": "+3.2%", "price": "9,850"},
            {"ticker": "TLKM.JK", "name": "Telkom", "change": "+2.8%", "price": "3,920"},
            {"ticker": "ASII.JK", "name": "Astra", "change": "+2.1%", "price": "5,120"},
            {"ticker": "UNVR.JK", "name": "Unilever", "change": "+1.9%", "price": "3,450"},
            {"ticker": "BMRI.JK", "name": "Bank Mandiri", "change": "+1.7%", "price": "6,780"}
        ]
        
        for stock in gainers:
            with st.container():
                col_a, col_b = st.columns([2, 1])
                with col_a:
                    st.markdown(f"**{stock['ticker']}**")
                    st.caption(stock['name'])
                with col_b:
                    st.markdown(f"**{stock['price']}**")
                    st.markdown(f"<span style='color: #38a169'>{stock['change']}</span>", unsafe_allow_html=True)
                st.divider()
        
        st.markdown('<div class="sub-header" style="margin-top: 2rem;">📉 Top Losers</div>', unsafe_allow_html=True)
        
        # Sample top losers
        losers = [
            {"ticker": "INKP.JK", "name": "Indah Kiat", "change": "-2.3%", "price": "8,540"},
            {"ticker": "ANTM.JK", "name": "Aneka Tambang", "change": "-1.9%", "price": "1,890"},
            {"ticker": "PGAS.JK", "name": "Perusahaan Gas", "change": "-1.5%", "price": "1,560"}
        ]
        
        for stock in losers:
            with st.container():
                col_a, col_b = st.columns([2, 1])
                with col_a:
                    st.markdown(f"**{stock['ticker']}**")
                    st.caption(stock['name'])
                with col_b:
                    st.markdown(f"**{stock['price']}**")
                    st.markdown(f"<span style='color: #e53e3e'>{stock['change']}</span>", unsafe_allow_html=True)
                st.divider()
    
    st.divider()
    
    # Recent Analyses
    st.markdown('<div class="sub-header">📋 Recent Analyses</div>', unsafe_allow_html=True)
    
    if st.session_state.analysis_history:
        for analysis in st.session_state.analysis_history[-3:]:  # Last 3 analyses
            with st.container():
                col1, col2, col3 = st.columns([1, 2, 1])
                with col1:
                    st.markdown(f"**{analysis.get('ticker', 'N/A')}**")
                with col2:
                    st.markdown(f"{analysis.get('name', 'N/A')}")
                with col3:
                    render_recommendation_badge(analysis.get('recommendation', 'hold'))
                st.divider()
    else:
        st.info("No recent analyses. Analyze a stock to see history here.")

def render_stock_analysis(app, formatter):
    """Render detailed stock analysis page"""
    
    ticker = st.session_state.selected_ticker
    
    st.markdown(f'<div class="main-header">🔍 Stock Analysis: {ticker}</div>', unsafe_allow_html=True)
    
    # Loading state
    if st.session_state.analysis_result is None or st.session_state.analysis_result.get('ticker') != ticker:
        with st.spinner(f"Analyzing {ticker}..."):
            try:
                result = app.analyze_stock(ticker)
                st.session_state.analysis_result = result
                
                # Add to history
                history_entry = {
                    'ticker': ticker,
                    'name': result.get('metadata', {}).get('name', 'Unknown'),
                    'price': result.get('current_price', 0),
                    'recommendation': result.get('score', {}).get('recommendation', 'hold'),
                    'timestamp': datetime.now().isoformat()
                }
                st.session_state.analysis_history.append(history_entry)
                
            except Exception as e:
                st.error(f"Error analyzing {ticker}: {str(e)}")
                return
    
    result = st.session_state.analysis_result
    
    if 'error' in result:
        st.error(result['error'])
        return
    
    # Stock header
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown(f"""
        <h2 style="margin: 0; color: #2d3748;">
            {result.get('metadata', {}).get('name', 'N/A')}
        </h2>
        <p style="margin: 0; color: #718096;">
            {result.get('metadata', {}).get('sector', 'N/A')} | {result.get('metadata', {}).get('industry', 'N/A')}
        </p>
        """, unsafe_allow_html=True)
    
    with col2:
        current_price = result.get('current_price', 0)
        price_formatted = formatter.format_currency(current_price)
        st.markdown(f"""
        <h1 style="margin: 0; color: #2d3748; text-align: right;">
            {price_formatted}
        </h1>
        """, unsafe_allow_html=True)
    
    with col3:
        score = result.get('score', {}).get('total_score', 0)
        recommendation = result.get('score', {}).get('recommendation', 'hold')
        render_recommendation_badge(recommendation)
        st.markdown(f"""
        <div style="text-align: right; margin-top: 5px;">
            <span style="color: #718096; font-size: 0.9rem;">
                Score: {score}/10
            </span>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Main analysis tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Overview", 
        "📊 Fundamental", 
        "📉 Technical", 
        "💰 Dividend", 
        "🎯 Recommendation"
    ])
    
    with tab1:
        render_overview_tab(result, formatter)
    
    with tab2:
        render_fundamental_tab(result, formatter)
    
    with tab3:
        render_technical_tab(result, formatter)
    
    with tab4:
        render_dividend_tab(result, formatter)
    
    with tab5:
        render_recommendation_tab(result, formatter)
    
    st.divider()
    
    # AI Summary
    st.markdown("### 🤖 AI Summary & Insights")
    st.markdown(result.get('summary', 'No summary available'))

def render_overview_tab(result, formatter):
    """Render overview tab"""
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Price chart
        st.markdown("#### Price Chart")
        
        # Get price data (in real app, this would come from result)
        try:
            stock = yf.Ticker(st.session_state.selected_ticker)
            hist = stock.history(period="6mo")
            
            if not hist.empty:
                fig = go.Figure(data=[go.Candlestick(
                    x=hist.index,
                    open=hist['Open'],
                    high=hist['High'],
                    low=hist['Low'],
                    close=hist['Close'],
                    name='Price'
                )])
                
                fig.update_layout(
                    title=f'{st.session_state.selected_ticker} Price',
                    yaxis_title='Price',
                    xaxis_title='Date',
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No price data available")
        except:
            st.info("Price chart requires active internet connection")
    
    with col2:
        # Key metrics
        st.markdown("#### Key Metrics")
        
        metrics = [
            ("Market Cap", result.get('fundamental', {}).get('fundamental', {}).get('market_cap')),
            ("P/E Ratio", result.get('fundamental', {}).get('fundamental', {}).get('pe_ratio')),
            ("P/B Ratio", result.get('fundamental', {}).get('fundamental', {}).get('pb_ratio')),
            ("ROE", result.get('fundamental', {}).get('fundamental', {}).get('roe')),
            ("Dividend Yield", result.get('dividend', {}).get('dividend', {}).get('dividend_yield'))
        ]
        
        for label, value in metrics:
            col_a, col_b = st.columns([2, 1])
            with col_a:
                st.markdown(f"**{label}**")
            with col_b:
                if value is not None:
                    if label in ["ROE", "Dividend Yield"]:
                        st.markdown(f"{formatter.format_percentage(value)}")
                    elif label == "Market Cap":
                        st.markdown(f"{formatter.format_currency(value)}")
                    else:
                        st.markdown(f"{formatter.format_number(value)}")
                else:
                    st.markdown("N/A")
            st.divider()
        
        # Trend indicator
        st.markdown("#### Trend Analysis")
        trend = result.get('technical', {}).get('technical', {}).get('trend_direction')
        if trend:
            render_trend_indicator(trend)
        else:
            st.info("No trend data")
    
    # Quick stats row
    st.markdown("#### Quick Stats")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "52W High",
            formatter.format_currency(10000),  # Example value
            delta="+5.2%"
        )
    
    with col2:
        st.metric(
            "52W Low",
            formatter.format_currency(8500),  # Example value
            delta="-3.1%"
        )
    
    with col3:
        st.metric(
            "Avg Volume",
            "25.4M",
            delta="+2.3%"
        )
    
    with col4:
        st.metric(
            "Beta",
            "1.2",
            delta="0.1"
        )

def render_fundamental_tab(result, formatter):
    """Render fundamental analysis tab"""
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("#### 📊 Valuation Metrics")
        
        valuation_metrics = [
            ("P/E Ratio", result.get('fundamental', {}).get('fundamental', {}).get('pe_ratio')),
            ("P/B Ratio", result.get('fundamental', {}).get('fundamental', {}).get('pb_ratio')),
            ("P/S Ratio", result.get('fundamental', {}).get('fundamental', {}).get('ps_ratio')),
            ("EV/EBITDA", result.get('fundamental', {}).get('fundamental', {}).get('ev_to_ebitda')),
            ("Market Cap", result.get('fundamental', {}).get('fundamental', {}).get('market_cap'))
        ]
        
        for label, value in valuation_metrics:
            with st.container():
                col_a, col_b, col_c = st.columns([2, 1, 1])
                with col_a:
                    st.markdown(f"**{label}**")
                with col_b:
                    if value is not None:
                        if label == "Market Cap":
                            st.markdown(formatter.format_currency(value))
                        else:
                            st.markdown(formatter.format_number(value))
                    else:
                        st.markdown("N/A")
                with col_c:
                    # Simple rating
                    if value is not None:
                        if label == "P/E Ratio" and value < 15:
                            st.success("Good")
                        elif label == "P/B Ratio" and value < 1.5:
                            st.success("Good")
                        else:
                            st.info("Check")
            st.divider()
        
        st.markdown("#### 💰 Financial Health")
        
        health_metrics = [
            ("Debt/Equity", result.get('fundamental', {}).get('fundamental', {}).get('debt_to_equity')),
            ("Current Ratio", result.get('fundamental', {}).get('fundamental', {}).get('current_ratio')),
            ("Quick Ratio", result.get('fundamental', {}).get('fundamental', {}).get('quick_ratio'))
        ]
        
        for label, value in health_metrics:
            with st.container():
                col_a, col_b, col_c = st.columns([2, 1, 1])
                with col_a:
                    st.markdown(f"**{label}**")
                with col_b:
                    st.markdown(formatter.format_number(value) if value else "N/A")
                with col_c:
                    if value is not None:
                        if label == "Debt/Equity" and value < 0.5:
                            st.success("Good")
                        elif label == "Current Ratio" and value > 1.5:
                            st.success("Good")
                        else:
                            st.warning("Watch")
            st.divider()
    
    with col2:
        st.markdown("#### 📈 Profitability")
        
        profit_metrics = [
            ("ROE", result.get('fundamental', {}).get('fundamental', {}).get('roe')),
            ("ROA", result.get('fundamental', {}).get('fundamental', {}).get('roa')),
            ("Gross Margin", result.get('fundamental', {}).get('fundamental', {}).get('gross_margin')),
            ("Net Margin", result.get('fundamental', {}).get('fundamental', {}).get('net_margin'))
        ]
        
        for label, value in profit_metrics:
            with st.container():
                col_a, col_b, col_c = st.columns([2, 1, 1])
                with col_a:
                    st.markdown(f"**{label}**")
                with col_b:
                    st.markdown(formatter.format_percentage(value) if value else "N/A")
                with col_c:
                    if value is not None:
                        if label == "ROE" and value > 0.15:
                            st.success("Good")
                        elif label == "Net Margin" and value > 0.1:
                            st.success("Good")
                        else:
                            st.info("Avg")
            st.divider()
        
        st.markdown("#### 🚀 Growth Metrics")
        
        growth_metrics = [
            ("Revenue Growth", result.get('fundamental', {}).get('fundamental', {}).get('revenue_growth_yoy')),
            ("EPS Growth", result.get('fundamental', {}).get('fundamental', {}).get('eps_growth')),
            ("Dividend Growth", result.get('dividend', {}).get('dividend', {}).get('dividend_growth_5y'))
        ]
        
        for label, value in growth_metrics:
            with st.container():
                col_a, col_b, col_c = st.columns([2, 1, 1])
                with col_a:
                    st.markdown(f"**{label}**")
                with col_b:
                    st.markdown(formatter.format_percentage(value) if value else "N/A")
                with col_c:
                    if value is not None and value > 0:
                        st.success("Positive")
                    elif value is not None and value < 0:
                        st.error("Negative")
                    else:
                        st.info("Stable")
            st.divider()
        
        # Fundamental Score
        st.markdown("#### 🏆 Fundamental Score")
        
        # Radar chart
        fig = create_fundamental_radar_chart(result.get('fundamental', {}))
        st.plotly_chart(fig, use_container_width=True)

def render_technical_tab(result, formatter):
    """Render technical analysis tab"""
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Technical charts
        st.markdown("#### 📊 Technical Charts")
        
        tab1, tab2, tab3 = st.tabs(["Price & MAs", "RSI", "MACD"])
        
        with tab1:
            # Get price data for chart
            try:
                stock = yf.Ticker(st.session_state.selected_ticker)
                hist = stock.history(period="6mo")
                
                if not hist.empty:
                    # Add moving averages
                    hist['MA20'] = hist['Close'].rolling(20).mean()
                    hist['MA50'] = hist['Close'].rolling(50).mean()
                    hist['MA200'] = hist['Close'].rolling(200).mean()
                    
                    fig = go.Figure()
                    
                    # Add candlestick
                    fig.add_trace(go.Candlestick(
                        x=hist.index,
                        open=hist['Open'],
                        high=hist['High'],
                        low=hist['Low'],
                        close=hist['Close'],
                        name='Price'
                    ))
                    
                    # Add moving averages
                    fig.add_trace(go.Scatter(
                        x=hist.index,
                        y=hist['MA20'],
                        name='MA20',
                        line=dict(color='orange', width=1)
                    ))
                    
                    fig.add_trace(go.Scatter(
                        x=hist.index,
                        y=hist['MA50'],
                        name='MA50',
                        line=dict(color='blue', width=1)
                    ))
                    
                    fig.add_trace(go.Scatter(
                        x=hist.index,
                        y=hist['MA200'],
                        name='MA200',
                        line=dict(color='red', width=2)
                    ))
                    
                    fig.update_layout(
                        title='Price with Moving Averages',
                        yaxis_title='Price',
                        height=400
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No price data available")
            except:
                st.info("Chart requires internet connection")
        
        with tab2:
            # RSI chart
            try:
                stock = yf.Ticker(st.session_state.selected_ticker)
                hist = stock.history(period="6mo")
                
                if not hist.empty and len(hist) > 14:
                    # Calculate RSI
                    delta = hist['Close'].diff()
                    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
                    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
                    rs = gain / loss
                    hist['RSI'] = 100 - (100 / (1 + rs))
                    
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=hist.index,
                        y=hist['RSI'],
                        name='RSI',
                        line=dict(color='purple', width=2)
                    ))
                    
                    # Add horizontal lines
                    fig.add_hline(y=70, line_dash="dash", line_color="red")
                    fig.add_hline(y=30, line_dash="dash", line_color="green")
                    fig.add_hline(y=50, line_dash="dot", line_color="gray")
                    
                    fig.update_layout(
                        title='RSI (14)',
                        yaxis_title='RSI',
                        yaxis_range=[0, 100],
                        height=300
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Not enough data for RSI calculation")
            except:
                st.info("RSI chart requires internet connection")
        
        with tab3:
            # MACD chart
            try:
                stock = yf.Ticker(st.session_state.selected_ticker)
                hist = stock.history(period="6mo")
                
                if not hist.empty and len(hist) > 26:
                    # Calculate MACD
                    exp12 = hist['Close'].ewm(span=12, adjust=False).mean()
                    exp26 = hist['Close'].ewm(span=26, adjust=False).mean()
                    macd = exp12 - exp26
                    signal = macd.ewm(span=9, adjust=False).mean()
                    histogram = macd - signal
                    
                    fig = go.Figure()
                    
                    fig.add_trace(go.Scatter(
                        x=hist.index,
                        y=macd,
                        name='MACD',
                        line=dict(color='blue', width=2)
                    ))
                    
                    fig.add_trace(go.Scatter(
                        x=hist.index,
                        y=signal,
                        name='Signal',
                        line=dict(color='red', width=2)
                    ))
                    
                    # Add histogram with colors
                    colors = ['green' if h >= 0 else 'red' for h in histogram]
                    fig.add_trace(go.Bar(
                        x=hist.index,
                        y=histogram,
                        name='Histogram',
                        marker_color=colors,
                        opacity=0.5
                    ))
                    
                    fig.update_layout(
                        title='MACD',
                        yaxis_title='MACD',
                        height=300
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Not enough data for MACD calculation")
            except:
                st.info("MACD chart requires internet connection")
    
    with col2:
        st.markdown("#### 📈 Technical Indicators")
        
        technical = result.get('technical', {}).get('technical', {})
        
        indicators = [
            ("Trend", technical.get('trend_direction')),
            ("RSI", technical.get('rsi')),
            ("RSI Signal", technical.get('rsi_signal')),
            ("MACD", technical.get('macd')),
            ("MACD Signal", technical.get('macd_signal_line')),
            ("Support", technical.get('support_level')),
            ("Resistance", technical.get('resistance_level')),
            ("Volatility", "12.5%")  # Example
        ]
        
        for label, value in indicators:
            with st.container():
                col_a, col_b = st.columns([2, 1])
                with col_a:
                    st.markdown(f"**{label}**")
                with col_b:
                    if value is not None:
                        if label == "Trend":
                            render_trend_indicator(value)
                        elif label in ["Support", "Resistance"]:
                            st.markdown(formatter.format_currency(value) if value else "N/A")
                        elif label == "RSI":
                            if value:
                                st.markdown(f"{float(value):.2f}")
                                # Color code RSI
                                if float(value) < 30:
                                    st.markdown("<span style='color: green'>Oversold</span>", unsafe_allow_html=True)
                                elif float(value) > 70:
                                    st.markdown("<span style='color: red'>Overbought</span>", unsafe_allow_html=True)
                                else:
                                    st.markdown("<span style='color: orange'>Neutral</span>", unsafe_allow_html=True)
                            else:
                                st.markdown("N/A")
                        else:
                            st.markdown(str(value))
                    else:
                        st.markdown("N/A")
                st.divider()
        
        st.markdown("#### 🎯 Trading Signals")
        
        signals = result.get('signals', [])
        
        if signals:
            for signal in signals[:5]:  # Show first 5 signals
                signal_type = signal.get('type', '')
                indicator = signal.get('indicator', '')
                strength = signal.get('strength', '')
                message = signal.get('message', '')
                
                # Determine color based on signal type
                if signal_type == 'BUY':
                    color = 'green'
                    icon = '🟢'
                elif signal_type == 'SELL':
                    color = 'red'
                    icon = '🔴'
                else:
                    color = 'gray'
                    icon = '⚪'
                
                st.markdown(f"""
                <div style="
                    background-color: {color}10;
                    border-left: 4px solid {color};
                    padding: 10px;
                    margin: 5px 0;
                    border-radius: 4px;
                ">
                    <strong>{icon} {signal_type}</strong> via {indicator} ({strength})<br>
                    <small>{message}</small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No trading signals generated")

def render_dividend_tab(result, formatter):
    """Render dividend analysis tab"""
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("#### 💰 Dividend Information")
        
        dividend_data = result.get('dividend', {}).get('dividend', {})
        
        metrics = [
            ("Dividend Yield", dividend_data.get('dividend_yield')),
            ("Dividend Per Share", dividend_data.get('dividend_per_share')),
            ("Payout Ratio", dividend_data.get('payout_ratio')),
            ("5-Year Avg Yield", dividend_data.get('five_year_avg_yield')),
            ("Dividend Growth (5Y)", dividend_data.get('dividend_growth_5y'))
        ]
        
        for label, value in metrics:
            with st.container():
                col_a, col_b, col_c = st.columns([2, 1, 1])
                with col_a:
                    st.markdown(f"**{label}**")
                with col_b:
                    if value is not None:
                        if label in ["Dividend Yield", "5-Year Avg Yield", "Payout Ratio", "Dividend Growth (5Y)"]:
                            st.markdown(formatter.format_percentage(value))
                        elif label == "Dividend Per Share":
                            st.markdown(formatter.format_currency(value))
                        else:
                            st.markdown(formatter.format_number(value))
                    else:
                        st.markdown("N/A")
                with col_c:
                    if value is not None:
                        if label == "Dividend Yield" and value > 0.05:
                            st.success("High")
                        elif label == "Payout Ratio" and value < 0.8:
                            st.success("Sustainable")
                        elif label == "Dividend Growth (5Y)" and value > 0:
                            st.success("Growing")
                        else:
                            st.info("Check")
                st.divider()
        
        # Dividend history chart (example)
        st.markdown("#### 📅 Dividend History")
        
        # Example dividend data
        dates = ['2020', '2021', '2022', '2023', '2024']
        dividends = [150, 160, 165, 170, 175]  # Example dividends per share
        
        fig = go.Figure(data=go.Bar(
            x=dates,
            y=dividends,
            marker_color='#48bb78'
        ))
        
        fig.update_layout(
            title='Dividend Per Share (Historical)',
            yaxis_title='Dividend (IDR)',
            height=300
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### 🏆 Dividend Quality")
        
        # Dividend quality assessment
        yield_val = dividend_data.get('dividend_yield', 0) or 0
        payout_val = dividend_data.get('payout_ratio', 0) or 0
        
        # Score calculation (simplified)
        score = 0
        if yield_val > 0.05:
            score += 3
        elif yield_val > 0.03:
            score += 2
        elif yield_val > 0:
            score += 1
        
        if payout_val < 0.6:
            score += 3
        elif payout_val < 0.8:
            score += 2
        elif payout_val < 1:
            score += 1
        
        total_score = min(score, 6)
        
        # Quality rating
        if total_score >= 5:
            rating = "🟢 Excellent"
            description = "Strong and sustainable dividend"
        elif total_score >= 3:
            rating = "🟡 Good"
            description = "Reasonable dividend with good coverage"
        elif total_score >= 1:
            rating = "🟠 Fair"
            description = "Dividend exists but could be better"
        else:
            rating = "🔴 Poor"
            description = "Weak or no dividend"
        
        st.markdown(f"""
        <div style="text-align: center; padding: 20px; background: #f7fafc; border-radius: 10px;">
            <h1 style="margin: 0; color: #2d3748;">{total_score}/6</h1>
            <h3 style="margin: 10px 0; color: #4a5568;">{rating}</h3>
            <p style="margin: 0; color: #718096;">{description}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        st.markdown("#### 📊 Comparison")
        
        # Comparison with sector average
        comparison_data = {
            "Metric": ["Dividend Yield", "Payout Ratio", "Growth (5Y)"],
            "This Stock": [
                f"{formatter.format_percentage(yield_val)}",
                f"{formatter.format_percentage(payout_val)}",
                f"{formatter.format_percentage(dividend_data.get('dividend_growth_5y', 0) or 0)}"
            ],
            "Sector Avg": ["3.2%", "65%", "8.2%"]
        }
        
        df_comparison = pd.DataFrame(comparison_data)
        st.dataframe(df_comparison, use_container_width=True, hide_index=True)

def render_recommendation_tab(result, formatter):
    """Render recommendation tab"""
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("#### 🎯 Investment Recommendation")
        
        score_data = result.get('score', {})
        
        # Recommendation details
        recommendation = score_data.get('recommendation', 'hold')
        total_score = score_data.get('total_score', 0)
        confidence = score_data.get('confidence', 'medium')
        risk_level = score_data.get('risk_level', 'medium')
        time_horizon = score_data.get('time_horizon', 'medium')
        strategy = score_data.get('strategy', 'balanced')
        
        # Render recommendation badge
        render_recommendation_badge(recommendation)
        
        st.divider()
        
        # Score breakdown
        st.markdown("#### 📊 Score Breakdown")
        
        detail_scores = score_data.get('detail_scores', {})
        
        if detail_scores:
            for category, score_info in detail_scores.items():
                if isinstance(score_info, dict):
                    score_val = score_info.get('score', 0)
                    max_score = score_info.get('max_score', 10)
                else:
                    score_val = score_info
                    max_score = 10
                
                percentage = (score_val / max_score) * 100 if max_score > 0 else 0
                
                # Determine color
                if percentage >= 70:
                    color = '#38a169'
                elif percentage >= 50:
                    color = '#ecc94b'
                else:
                    color = '#e53e3e'
                
                st.markdown(f"**{category.replace('_', ' ').title()}**")
                st.markdown(f"""
                <div style="
                    background: #e2e8f0;
                    border-radius: 10px;
                    height: 20px;
                    margin: 5px 0 15px 0;
                ">
                    <div style="
                        background: {color};
                        width: {percentage}%;
                        height: 100%;
                        border-radius: 10px;
                        text-align: right;
                        padding-right: 10px;
                        color: white;
                        font-size: 0.8rem;
                        line-height: 20px;
                        font-weight: 600;
                    ">
                        {score_val}/{max_score}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        st.divider()
        
        # Investment rationale
        st.markdown("#### 📝 Investment Rationale")
        
        fundamental = result.get('fundamental', {})
        technical = result.get('technical', {})
        
        strengths = []
        weaknesses = []
        
        # Check fundamental strengths
        pe_ratio = fundamental.get('fundamental', {}).get('pe_ratio')
        if pe_ratio and pe_ratio < 15:
            strengths.append("Valuasi menarik (PER rendah)")
        
        roe = fundamental.get('fundamental', {}).get('roe')
        if roe and roe > 0.15:
            strengths.append("Profitabilitas tinggi (ROE baik)")
        
        # Check technical strengths
        trend = technical.get('technical', {}).get('trend_direction')
        if trend in ['bullish', 'strong_bullish']:
            strengths.append("Trend teknikal bullish")
        
        # Check weaknesses
        debt_ratio = fundamental.get('fundamental', {}).get('debt_to_equity')
        if debt_ratio and debt_ratio > 1:
            weaknesses.append("Rasio utang tinggi")
        
        if strengths:
            st.markdown("**✅ Strengths:**")
            for strength in strengths:
                st.markdown(f"- {strength}")
        
        if weaknesses:
            st.markdown("**⚠️ Weaknesses:**")
            for weakness in weaknesses:
                st.markdown(f"- {weakness}")
    
    with col2:
        st.markdown("#### 📈 Investment Score")
        
        # Gauge chart
        fig = create_recommendation_gauge(total_score, 10)
        st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # Risk assessment
        st.markdown("#### ⚠️ Risk Assessment")
        
        risk_colors = {
            'low': ('🟢 RENDAH', 'background: #c6f6d5; color: #22543d;'),
            'medium': ('🟡 SEDANG', 'background: #feebc8; color: #744210;'),
            'high': ('🔴 TINGGI', 'background: #fed7d7; color: #742a2a;')
        }
        
        risk_text, risk_style = risk_colors.get(risk_level.lower(), ('N/A', ''))
        
        st.markdown(f"""
        <div style="
            {risk_style}
            padding: 10px;
            border-radius: 5px;
            text-align: center;
            font-weight: 600;
            margin: 10px 0;
        ">
            {risk_text}
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"**Confidence:** {confidence.upper()}")
        st.markdown(f"**Time Horizon:** {time_horizon}")
        st.markdown(f"**Strategy:** {strategy}")
        
        st.divider()
        
        # Action plan
        st.markdown("#### 📋 Action Plan")
        
        if recommendation == 'strong_buy':
            st.success("""
            **Recommended Actions:**
            1. Pertimbangkan untuk membeli
            2. Bisa dialokasikan sebagai core holding
            3. Bisa ditambah jika ada koreksi
            """)
        elif recommendation == 'buy':
            st.info("""
            **Recommended Actions:**
            1. Bisa dibeli untuk portfolio
            2. Monitor level support untuk entry yang baik
            3. Diversifikasi dengan saham lain
            """)
        elif recommendation == 'hold':
            st.warning("""
            **Recommended Actions:**
            1. Tahan posisi yang ada
            2. Jangan menambah alokasi
            3. Monitor perkembangan fundamental
            """)
        elif recommendation in ['sell', 'strong_sell']:
            st.error("""
            **Recommended Actions:**
            1. Pertimbangkan untuk mengurangi
            2. Cari opportunity untuk switch
            3. Hindari average down
            """)

def render_portfolio():
    """Render portfolio management page"""
    
    st.markdown('<div class="main-header">💰 Portfolio Management</div>', unsafe_allow_html=True)
    
    # Portfolio summary
    if st.session_state.portfolio:
        total_value = sum(p['current_value'] for p in st.session_state.portfolio.values())
        total_investment = sum(p['investment'] for p in st.session_state.portfolio.values())
        total_pnl = total_value - total_investment
        pnl_percentage = (total_pnl / total_investment * 100) if total_investment > 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Value", f"Rp {total_value:,.0f}")
        
        with col2:
            st.metric("Total Investment", f"Rp {total_investment:,.0f}")
        
        with col3:
            st.metric("Total P&L", f"Rp {total_pnl:,.0f}")
        
        with col4:
            st.metric("Return %", f"{pnl_percentage:.2f}%", 
                     delta=f"{pnl_percentage:.2f}%")
        
        st.divider()
        
        # Portfolio holdings
        st.markdown("#### 📋 Portfolio Holdings")
        
        for ticker, data in st.session_state.portfolio.items():
            col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
            
            with col1:
                st.markdown(f"**{ticker}**")
                st.markdown(f"{data.get('name', 'N/A')}")
            
            with col2:
                st.markdown(f"**Shares**")
                st.markdown(f"{data['shares']}")
            
            with col3:
                st.markdown(f"**Avg Price**")
                st.markdown(f"Rp {data['buy_price']:,.0f}")
            
            with col4:
                st.markdown(f"**Current**")
                st.markdown(f"Rp {data['current_price']:,.0f}")
            
            with col5:
                pnl = data['pnl']
                pnl_percent = data['pnl_percent']
                color = "green" if pnl >= 0 else "red"
                st.markdown(f"**P&L**")
                st.markdown(f"<span style='color: {color}'>Rp {pnl:,.0f} ({pnl_percent:.1f}%)</span>", 
                          unsafe_allow_html=True)
            
            st.divider()
        
        # Portfolio allocation chart
        st.markdown("#### 📊 Portfolio Allocation")
        
        if st.session_state.portfolio:
            tickers = list(st.session_state.portfolio.keys())
            values = [st.session_state.portfolio[t]['current_value'] for t in tickers]
            
            fig = px.pie(
                names=tickers,
                values=values,
                title="Portfolio Allocation by Stock"
            )
            
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Your portfolio is empty. Add stocks to get started.")
    
    # Add to portfolio form
    st.markdown("#### ➕ Add to Portfolio")
    
    with st.form("add_to_portfolio"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            ticker = st.text_input("Stock Ticker", placeholder="BBCA.JK")
        
        with col2:
            shares = st.number_input("Shares", min_value=1, value=100)
        
        with col3:
            buy_price = st.number_input("Buy Price", min_value=0.0, value=0.0)
        
        submitted = st.form_submit_button("Add to Portfolio", type="primary")
        
        if submitted and ticker and shares > 0 and buy_price > 0:
            # Get current price
            try:
                stock = yf.Ticker(ticker)
                current_price = stock.history(period='1d')['Close'].iloc[-1]
                
                st.session_state.portfolio[ticker] = {
                    'shares': shares,
                    'buy_price': buy_price,
                    'current_price': current_price,
                    'investment': shares * buy_price,
                    'current_value': shares * current_price,
                    'pnl': (current_price - buy_price) * shares,
                    'pnl_percent': ((current_price - buy_price) / buy_price * 100) if buy_price > 0 else 0
                }
                
                st.success(f"Added {ticker} to portfolio")
                st.rerun()
            except Exception as e:
                st.error(f"Error adding {ticker}: {str(e)}")

def render_market_overview():
    """Render market overview page"""
    
    st.markdown('<div class="main-header">📈 Market Overview</div>', unsafe_allow_html=True)
    
    # Market indices
    st.markdown("#### 📊 Market Indices")
    
    indices = [
        {"name": "Jakarta Composite Index (JCI)", "value": "7,215.45", "change": "+15.32", "change_pct": "+0.21%"},
        {"name": "LQ45", "value": "975.23", "change": "+5.67", "change_pct": "+0.58%"},
        {"name": "IDX30", "value": "485.12", "change": "+3.45", "change_pct": "+0.72%"},
        {"name": "KOMPAS100", "value": "1,245.67", "change": "+8.90", "change_pct": "+0.72%"}
    ]
    
    for idx in indices:
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.markdown(f"**{idx['name']}**")
        with col2:
            st.markdown(f"**{idx['value']}**")
        with col3:
            color = "green" if idx['change'].startswith('+') else "red"
            st.markdown(f"<span style='color: {color}'>{idx['change']} ({idx['change_pct']})</span>", 
                       unsafe_allow_html=True)
        st.divider()
    
    # Sector performance
    st.markdown("#### 🏭 Sector Performance")
    
    sectors = [
        {"sector": "Finance", "change": "+1.8%", "top_stock": "BBCA"},
        {"sector": "Consumer", "change": "+1.2%", "top_stock": "UNVR"},
        {"sector": "Infrastructure", "change": "+0.9%", "top_stock": "TLKM"},
        {"sector": "Mining", "change": "-0.5%", "top_stock": "ANTM"},
        {"sector": "Property", "change": "-1.2%", "top_stock": "BSDE"}
    ]
    
    for sector in sectors:
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.markdown(f"**{sector['sector']}**")
        with col2:
            color = "green" if sector['change'].startswith('+') else "red"
            st.markdown(f"<span style='color: {color}'>{sector['change']}</span>", unsafe_allow_html=True)
        with col3:
            st.markdown(f"Top: {sector['top_stock']}")
        st.divider()
    
    # Market news (placeholder)
    st.markdown("#### 📰 Market News")
    
    news_items = [
        {"title": "BI Pertahankan Suku Bunga Acuan", "source": "Kontan", "time": "2 hours ago"},
        {"title": "Rupiah Menguat ke Level Rp15,600/USD", "source": "Bloomberg", "time": "3 hours ago"},
        {"title": "Emiten Properti Mulai Bangkit", "source": "Investor", "time": "5 hours ago"},
        {"title": "Dividen Tahunan Bank BUMN Capai Rp50 Triliun", "source": "CNBC", "time": "1 day ago"}
    ]
    
    for news in news_items:
        st.markdown(f"**{news['title']}**")
        st.markdown(f"*{news['source']} • {news['time']}*")
        st.divider()

def render_settings():
    """Render settings page"""
    
    st.markdown('<div class="main-header">⚙️ Settings</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 Analysis Settings")
        
        analysis_period = st.selectbox(
            "Default Analysis Period",
            ["1mo", "3mo", "6mo", "1y", "2y", "5y"],
            index=3
        )
        
        rsi_period = st.slider("RSI Period", 5, 30, 14)
        
        show_advanced = st.checkbox("Show Advanced Technical Indicators")
        
        st.markdown("#### 💰 Currency & Format")
        
        currency = st.selectbox(
            "Display Currency",
            ["IDR", "USD", "EUR", "SGD"],
            index=0
        )
        
        number_format = st.selectbox(
            "Number Format",
            ["Indonesian", "International", "Compact"],
            index=0
        )
    
    with col2:
        st.markdown("#### 🔔 Notifications")
        
        email_notifications = st.checkbox("Email Notifications", value=True)
        
        price_alerts = st.checkbox("Price Alerts", value=True)
        
        alert_threshold = st.slider("Price Alert Threshold (%)", 1, 20, 5)
        
        st.markdown("#### 🗂️ Data Management")
        
        auto_refresh = st.checkbox("Auto-refresh Data", value=True)
        
        cache_duration = st.slider("Cache Duration (hours)", 1, 24, 6)
        
        clear_cache = st.button("Clear Cache", type="secondary")
        
        if clear_cache:
            st.cache_resource.clear()
            st.success("Cache cleared successfully")
    
    # Save settings button
    if st.button("Save Settings", type="primary"):
        st.success("Settings saved successfully!")
        
        # In a real app, you would save these to a config file or database
        settings = {
            "analysis_period": analysis_period,
            "rsi_period": rsi_period,
            "currency": currency,
            "auto_refresh": auto_refresh,
            "cache_duration": cache_duration
        }
        
        # Save to session state
        st.session_state.settings = settings

# ============================================
# MAIN APP
# ============================================

def main():
    """Main Streamlit application"""
    
    # Load custom CSS
    load_custom_css()
    
    # Initialize session state
    initialize_session_state()
    
    # Initialize Warren AI
    app = initialize_warren_ai()
    formatter = get_formatter()
    
    if app is None:
        st.error("Failed to initialize Warren AI. Please check your installation.")
        return
    
    # Render sidebar and get navigation selection
    selected_nav = render_sidebar()
    
    # Render selected page
    if selected_nav == "📊 Dashboard":
        render_dashboard()
    elif selected_nav == "🔍 Stock Analysis":
        render_stock_analysis(app, formatter)
    elif selected_nav == "💰 Portfolio":
        render_portfolio()
    elif selected_nav == "📈 Market Overview":
        render_market_overview()
    elif selected_nav == "⚙️ Settings":
        render_settings()
    
    # Footer
    st.markdown("""
    <div style="text-align: center; color: #718096; font-size: 0.8rem; margin-top: 3rem; padding: 1rem 0; border-top: 1px solid #e2e8f0;">
        <p>Warren AI v2.0 | Disclaimer: This tool is for educational purposes only. Invest at your own risk.</p>
        <p>Data provided by Yahoo Finance. Analysis updated at {}</p>
    </div>
    """.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), unsafe_allow_html=True)

# ============================================
# RUN THE APP
# ============================================

if __name__ == "__main__":
    main()
