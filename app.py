import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

# --- 1. THIẾT LẬP HỆ THỐNG ---
st.set_page_config(page_title="HÃY CHỌN CÁ ĐÚNG v6.3.4", layout="wide")

st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 1.8rem !important; font-weight: bold; color: #007bff; }
    section[data-testid="stSidebar"] { width: 300px !important; }
    .stTable { border-radius: 12px; overflow: hidden; }
    </style>
    """, unsafe_allow_html=True)

if 'history_log' not in st.session_state: 
    st.session_state['history_log'] = []

def compute_rsi(data, window=14):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# --- 2. SIDEBAR: TRI KỶ & CẨM NANG ---
with st.sidebar:
    try:
        st.image("https://raw.githubusercontent.com/daohuudat/be-loc-sieu-cap/main/tri-ky.jpg", use_container_width=True)
    except:
        st.info("🖼️ [Đang nạp ảnh tri kỷ...]")
    
    st.header("🎮 ĐÀI CHỈ HUY")
    t_input = st.text_input("🔍 SOI MÃ CÁ", "VGC").upper()
    st.divider()
    
    st.header("📓 CẨM NANG CHIẾN THUẬT")
    with st.expander("📖 Giải mã thông số", expanded=True):
        st.markdown("""
        - **🛡️ Niềm tin > 80%:** Cá Lớn thực thụ.
        - **🌊 Sóng:** Mạnh khi Vol > 150% TB 20 phiên.
        - **🌡️ RSI:** >70 (Nóng), <30 (Lạnh).
        - **🍱 Thức ăn:** Dư địa % về giá cơ sở/MA20.
        """)

st.title("🚀 Bể Lọc v6.3.4: SIÊU CẤP VIP PRO")

# --- 3. TRẠM QUAN TRẮC VNI ---
inf_factor = 1.0 
try:
    vni = yf.download("^VNI", period="150d", progress=False)
    if not vni.empty:
        if isinstance(vni.columns, pd.MultiIndex): vni.columns = vni.columns.get_level_values(0)
        v_c = float(vni['Close'].iloc[-1])
        vh26 = vni['High'].rolling(26).max(); vl26 = vni['Low'].rolling(26).min()
        vh9 = vni['High'].rolling(9).max(); vl9 = vni['Low'].rolling(9).min()
        vsa = (((vh9+vl9)/2 + (vh26+vl26)/2)/2).shift(26).iloc[-1]
        inf_factor = 1.15 if v_c > vsa else 0.85
        st.info(f"🌊 Đại Dương: {'🟢 THẢ LƯỚI' if v_c > vsa else '🔴 ĐÁNH KẺNG'}")
except: pass

# --- 4. HỆ THỐNG TABS ---
tab_radar, tab_analysis, tab_history = st.tabs(["🎯 RADAR ELITE", "💎 CHI TIẾT SIÊU CÁ", "📓 SỔ VÀNG"])

with tab_radar:
    # (Giữ nguyên toàn bộ logic Radar v6.3.3)
    st.subheader("🤖 Top 20 Đệ Tử Cá")
    elite_20 = ["DGC", "MWG", "FPT", "TCB", "SSI", "HPG", "GVR", "CTR", "DBC", "VNM", "STB", "MBB", "ACB", "KBC", "VGC", "PVS", "PVD", "ANV", "VHC", "REE"]
    radar_list = []
    for tk in elite_20:
        try:
            d = yf.download(f"{tk}.VN", period="50d", progress=False)
            if not d.empty:
                if isinstance(d.columns, pd.MultiIndex): d.columns = d.columns.get_level_values(0)
                p_c = d['Close'].iloc[-1]
                v_now = d['Volume'].iloc[-1]; v_avg = d['Volume'].rolling(20).mean().iloc[-1]
                ma20 = d['Close'].rolling(20).mean().iloc[-1]
                radar_list.append({"Mã": tk, "Giá": f"{p_c:,.0f}", "Sóng": "🌊 Mạnh" if v_now > v_avg * 1.5 else "☕ Lặng", "Loại": "Cá Lớn 🐋" if p_c > ma20 and v_now > v_avg else "Cá Nhỏ 🐟"})
        except: continue
    st.table(pd.DataFrame(radar_list))

with tab_analysis:
    try:
        t_obj = yf.Ticker(f"{t_input}.VN")
        s_df = t_obj.history(period="1y")
        if isinstance(s_df.columns, pd.MultiIndex): s_df.columns = s_df.columns.get_level_values(0)
        curr_p = float(s_df['Close'].iloc[-1])
        
        s_df['RSI'] = compute_rsi(s_df['Close'])
        s_df['Vol_Avg'] = s_df['Volume'].rolling(20).mean()
        curr_rsi = s_df['RSI'].iloc[-1]
        
        try:
            fin = t_obj.quarterly_financials
            g_val = ((fin.loc['Total Revenue'].iloc[0] / fin.loc['Total Revenue'].iloc[4]) - 1)
            trust = int(min(100, (g_val * 100) + (50 if curr_p > s_df['Close'].rolling(50).mean().iloc[-1] else 0)))
        except: g_val = 0.1; trust = 65

        st.markdown(f"### 🛡️ Niềm tin {t_input}: {trust}% | RSI: {curr_rsi:.1f}")
        st.progress(max(0, min(trust / 100, 1.0)))

        # --- TINH CHỈNH MỤC GIÁ HIỆN TẠI TẠI ĐÂY ---
        c_price, c1, c2,