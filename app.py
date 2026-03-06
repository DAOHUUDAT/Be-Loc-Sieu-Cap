import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

# --- 1. MÁY BƠM TĂNG ÁP (Caching tầng cao) ---
@st.cache_data(ttl=600)
def load_all_radar_data(tickers):
    """Hút dữ liệu của tất cả mã trong Radar một lần duy nhất để tăng tốc"""
    try:
        # Tải gộp tất cả mã giúp giảm thời gian chờ đợi đáng kể
        data = yf.download([f"{t}.VN" for t in tickers], period="150d", progress=False, group_by='ticker')
        return data
    except:
        return None

@st.cache_data(ttl=600)
def load_ticker_data(ticker):
    """Máy bơm dự phòng cho Tab Chi tiết"""
    try:
        data = yf.download(f"{ticker}.VN", period="150d", progress=False)
        if not data.empty and isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
        return data
    except:
        return pd.DataFrame()

def compute_rsi_pro(data, window=14):
    """Tính toán nhiệt độ cá (RSI)"""
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

@st.cache_data(ttl=3600) # Dữ liệu BCTC lưu kho 1 tiếng
def load_vietstock_data():
    urls = [
        "https://github.com/DAOHUUDAT/Be-Loc-Sieu-Cap/raw/refs/heads/main/data/HOSE.xlsx",
        "https://github.com/DAOHUUDAT/Be-Loc-Sieu-Cap/raw/refs/heads/main/data/HNX.xlsx",
        "https://github.com/DAOHUUDAT/Be-Loc-Sieu-Cap/raw/refs/heads/main/data/UPCOM.xlsx"
    ]
    dfs = []
    for url in urls:
        try:
            df = pd.read_excel(url)
            df.columns = [str(c).strip() for c in df.columns]
            dfs.append(df.loc[:, ~df.columns.duplicated()]) # Xử lý trùng cột
        except: continue
    return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()

# Khởi động đại dương
vietstock_db = load_vietstock_data()

# --- 2. CẤU HÌNH GIAO DIỆN (Giữ nguyên phong cách của bro) ---
st.set_page_config(page_title="HÃY CHỌN CÁ ĐÚNG v6.3.15", layout="wide")

if 'selected_ticker' not in st.session_state:
    st.session_state.selected_ticker = "FPT"
if 'history_log' not in st.session_state: 
    st.session_state['history_log'] = []

st.title("🚀 Bể Lọc v6.3.15: HÃY CHỌN CÁ ĐÚNG")

# --- 3. QUAN TRẮC VN-INDEX ---
try:
    vni = yf.download("^VNI", period="150d", progress=False)
    if not vni.empty:
        if isinstance(vni.columns, pd.MultiIndex): vni.columns = vni.columns.get_level_values(0)
        v_c = float(vni['Close'].iloc[-1])
        st.info(f"🌊 Đại Dương: VN-Index đang ở {v_c:,.2f}")
except: v_c = 1200

# --- 4. HỆ THỐNG TABS TỐI ƯU ---
tab_radar, tab_analysis, tab_bctc, tab_history = st.tabs(["🎯 RADAR ELITE", "💎 CHI TIẾT SIÊU CÁ", "📊 MỔ XẺ BCTC", "📓 SỔ VÀNG"])

with tab_radar:
    st.subheader("🤖 Top 20 SIÊU CÁ (Hệ thống Radar)")
    elite_20 = ["DGC", "MWG", "FPT", "TCB", "SSI", "HPG", "GVR", "CTR", "DBC", "VNM", "STB", "MBB", "ACB", "KBC", "VGC", "PVS", "PVD", "ANV", "VHC", "REE"]
    
    # Nạp dữ liệu gộp giúp app chạy mượt hơn hẳn
    all_data = load_all_radar_data(elite_20)
    radar_list = []
    
    with st.spinner('Đang quét tín hiệu đại dương...'):
        for tk in elite_20:
            try:
                # Lấy dữ liệu từ bộ nhớ đệm gộp
                d = all_data[f"{tk}.VN"].dropna()
                if d.empty: continue
                
                p_c = d['Close'].iloc[-1]
                v_now = d['Volume'].iloc[-1]
                v_avg = d['Volume'].rolling(20).mean().iloc[-1]
                ma20 = d['Close'].rolling(20).mean().iloc[-1]
                ma50 = d['Close'].rolling(50).mean().iloc[-1]
                
                # Sức mạnh RS
                stock_perf = (p_c / d['Close'].iloc[-20]) - 1
                vni_perf = (v_c / vni['Close'].iloc[-20]) - 1 if not vni.empty else 0
                is_stronger = stock_perf > vni_perf
                
                # Nhiệt độ RSI
                curr_rsi = compute_rsi_pro(d['Close']).iloc[-1]
                temp = "🔥 Nóng" if curr_rsi > 70 else "❄️ Lạnh" if curr_rsi < 30 else "🌤️ Êm"
                
                # Phân loại cá dựa trên tiềm năng
                if p_c > ma20 and v_now > v_avg * 1.5 and is_stronger:
                    loai_ca, priority = "🚀 SIÊU CÁ", 1
                elif p_c > ma20 and p_c > ma50:
                    loai_ca, priority = "cá lớn 🐋", 2
                else:
                    loai_ca, priority = "cá nhỏ 🐟", 3
                
                radar_list.append({
                    "Mã": tk, "Giá": f"{p_c:,.0f}",
                    "Sóng": "🌊 Mạnh" if v_now > v_avg * 1.5 else "☕ Lặng",
                    "Nhiệt độ": temp, "Đại Dương": "💪 Khỏe" if is_stronger else "🐌 Yêu",
                    "Loại": loai_ca, "Thức ăn": f"{((ma20/p_c)-1)*100:+.1f}%" if p_c < ma20 else "✅ Đang no",
                    "priority": priority, "RS_Raw": stock_perf - vni_perf
                })
            except: continue

    df_radar = pd.DataFrame(radar_list).sort_values(by=["priority", "RS_Raw"], ascending=[True, False])
    
    # Hiển thị bảng chọn lọc
    selection = st.dataframe(
        df_radar.drop(columns=['priority', 'RS_Raw']), 
        use_container_width=True, hide_index=True,
        selection_mode="single-row", on_select="rerun"
    )

    if selection and len(selection.selection.rows) > 0:
        st.session_state.selected_ticker = df_radar.iloc[selection.selection.rows[0]]['Mã']
        st.toast(f"🎯 Đã khóa mục tiêu: {st.session_state.selected_ticker}")

with tab_analysis:
    # Đồng bộ mã cá từ Radar
    target = st.session_state.selected_ticker
    t_input = st.text_input("Mã cá mổ xẻ:", value=target, key="analysis_input").upper()
    
    if t_input != st.session_state.selected_ticker:
        st.session_state.selected_ticker = t_input
        st.rerun()

    # (Phần vẽ biểu đồ và tính toán của bro giữ nguyên tại đây...)
    st.write(f"Đang phân tích kỹ thuật cho: {t_input}")