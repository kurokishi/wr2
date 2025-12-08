# streamlit_app.py
import streamlit as st
import pandas as pd
from main import WarrenAI
from core.config import Config

# Page config
st.set_page_config(
    page_title="Warren AI - Advanced Stock Analysis",
    page_icon="📈",
    layout="wide"
)

# Initialize app
@st.cache_resource
def get_warren_ai():
    config = Config(data_provider='yahoo')
    return WarrenAI(config)

app = get_warren_ai()

# Sidebar
st.sidebar.title("Warren AI")
ticker = st.sidebar.text_input("Masukkan kode saham:", "BBCA.JK")
analyze_btn = st.sidebar.button("Analisis", type="primary")

# Main content
st.title("📈 Warren AI - Advanced Stock Analysis")

if analyze_btn and ticker:
    with st.spinner("Menganalisis..."):
        result = app.analyze_stock(ticker)
    
    # Tampilkan hasil dalam tab
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Summary", 
        "🔍 Fundamental", 
        "📈 Teknikal", 
        "🎯 Rekomendasi"
    ])
    
    with tab1:
        st.markdown(result['summary'])
    
    with tab2:
        fund_data = result['fundamental'].data
        df_fund = pd.DataFrame([fund_data['fundamental']])
        st.dataframe(df_fund, use_container_width=True)
    
    with tab3:
        tech_data = result['technical'].data
        # Tampilkan chart teknikal
        # ...
    
    with tab4:
        st.metric("Rekomendasi", result['score'].data['recommendation'])
        st.metric("Skor Total", result['score'].data['total_score'])
