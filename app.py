import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import random

@st.cache_data(ttl=3600)
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
            if df.columns.duplicated().any():
                cols = pd.Series(df.columns)
                for dupe in cols[cols.duplicated()].unique():
                    mask = cols == dupe
                    cols[mask] = [f"{dupe}_{i}" if i != 0 else dupe for i in range(mask.sum())]
                df.columns = cols
            dfs.append(df.dropna(how='all'))
        except:
            continue
    if dfs:
        combined_df = pd.concat(dfs, axis=0, ignore_index=True, sort=False)
        return combined_df.loc[:, ~combined_df.columns.duplicated()]
    return pd.DataFrame()

vietstock_db = load_vietstock_data()
COL_MAP = {str(c).lower(): c for c in vietstock_db.columns} if not vietstock_db.empty else {}

def quick_find_col(keyword):
    for k, v in COL_MAP.items():
        if keyword.lower() in k: return v
    return None

def compute_rsi(data, window=14):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# --- CẤU HÌNH GIAO DIỆN ---
st.set_page_config(page_title="HÃY CHỌN CÁ ĐÚNG v6.3.15", layout="wide")

if 'history_log' not in st.session_state:
    st.session_state['history_log'] = []
if 'selected_ticker' not in st.session_state:
    st.session_state['selected_ticker'] = "FPT"

# --- SIDEBAR ---
with st.sidebar:
    st.header("🎮 ĐÀI CHỈ HUY")
    t_input = st.text_input("🔍 SOI MÃ CÁ", st.session_state.selected_ticker).upper()
    st.divider()
    st.info("💡 Mẹo: Click chọn cá ở Tab Radar để xem chi tiết ngay lập tức!")

# --- TRẠM QUAN TRẮC ĐẠI DƯƠNG ---
inf_factor = 1.0
v_c = 0
vni = pd.DataFrame()
try:
    vni = yf.download("^VNI", period="150d", progress=False)
    if not vni.empty:
        if isinstance(vni.columns, pd.MultiIndex): vni.columns = vni.columns.get_level_values(0)
        v_c = float(vni['Close'].iloc[-1])
        vh26 = vni['High'].rolling(26).max(); vl26 = vni['Low'].rolling(26).min()
        vsa = (((vni['High'].rolling(9).max()+vni['Low'].rolling(9).min())/2 + (vh26+vl26)/2)/2).shift(26).iloc[-1]
        inf_factor = 1.15 if v_c > vsa else 0.85
        st.info(f"🌊 Đại Dương: {'🟢 THẢ LƯỚI' if v_c > vsa else '🔴 ĐÁNH KẺNG'} | Hệ số: {inf_factor}x")
except: pass

tab_radar, tab_analysis, tab_bctc, tab_history = st.tabs(["🎯 RADAR ELITE", "💎 CHI TIẾT SIÊU CÁ", "📊 MỔ XẺ BCTC", "📓 SỔ VÀNG"])

with tab_radar:
    st.subheader("🤖 Top 20 SIÊU CÁ")
    elite_20 = ["DGC", "MWG", "FPT", "TCB", "SSI", "HPG", "GVR", "CTR", "DBC", "VNM", "STB", "MBB", "ACB", "KBC", "VGC", "PVS", "PVD", "ANV", "VHC", "REE"]
    radar_list = []
    
    with st.spinner('🔭 Đang quét tín hiệu siêu cá...'):
        for tk in elite_20:
            try:
                d = yf.download(f"{tk}.VN", period="100d", progress=False)
                if not d.empty:
                    if isinstance(d.columns, pd.MultiIndex): d.columns = d.columns.get_level_values(0)
                    p_c = d['Close'].iloc[-1]
                    v_now, v_avg = d['Volume'].iloc[-1], d['Volume'].rolling(20).mean().iloc[-1]
                    ma20, ma50 = d['Close'].rolling(20).mean().iloc[-1], d['Close'].rolling(50).mean().iloc[-1]
                    
                    curr_rsi = compute_rsi(d['Close']).iloc[-1]
                    stock_perf = (p_c / d['Close'].iloc[-20]) - 1
                    vni_perf = (v_c / vni['Close'].iloc[-20]) - 1 if not vni.empty else 0
                    is_stronger = stock_perf > vni_perf

                    if p_c > ma20 and v_now > v_avg * 1.2 and is_stronger:
                        loai, pri = "🚀 SIÊU CÁ", 1
                    elif p_c > ma20 and p_c > ma50:
                        loai, pri = "Cá Lớn 🐋", 2
                    else:
                        loai, pri = "Cá Nhỏ 🐟", 4

                    radar_list.append({
                        "Mã": tk, "Giá": f"{p_c:,.0f}", "Sóng": "🌊 Mạnh" if v_now > v_avg * 1.5 else "☕ Lặng",
                        "Nhiệt độ": "🔥 Nóng" if curr_rsi > 70 else "❄️ Lạnh" if curr_rsi < 30 else "🌤️ Êm",
                        "Đại Dương": "💪 Khỏe" if is_stronger else "🐌 Yếu", "Loại": loai, "priority": pri
                    })
            except: continue

    df_radar = pd.DataFrame(radar_list).sort_values("priority")
    sel = st.dataframe(df_radar.drop(columns=['priority']), use_container_width=True, hide_index=True, selection_mode="single-row", on_select="rerun")
    
    if len(sel.selection.rows) > 0:
        st.session_state.selected_ticker = df_radar.iloc[sel.selection.rows[0]]['Mã']
        st.toast(f"🎯 Khóa mục tiêu: {st.session_state.selected_ticker}")

with tab_analysis:
    t_curr = st.text_input("Mổ xẻ mã:", value=st.session_state.selected_ticker).upper()
    try:
        t_obj = yf.Ticker(f"{t_curr}.VN")
        s_df = t_obj.history(period="1y")
        if isinstance(s_df.columns, pd.MultiIndex): s_df.columns = s_df.columns.get_level_values(0)
        curr_p = float(s_df['Close'].iloc[-1])
        
        # Biểu đồ tài chính 5 quý
        fin_q = t_obj.quarterly_financials
        if not fin_q.empty:
            st.subheader("📊 Doanh thu & Lợi nhuận (Tỷ VNĐ)")
            q_rev = (fin_q.loc['Total Revenue'].iloc[:5][::-1]) / 1e9
            fig_fin = go.Figure()
            fig_fin.add_trace(go.Bar(x=q_rev.index.astype(str), y=q_rev, name='Doanh thu', marker_color='#007bff'))
            st.plotly_chart(fig_fin, use_container_width=True)

        # Biểu đồ kỹ thuật
        st.subheader(f"📈 Phân tích kỹ thuật {t_curr}")
        fig = go.Figure(data=[go.Candlestick(x=s_df.index, open=s_df['Open'], high=s_df['High'], low=s_df['Low'], close=s_df['Close'])])
        fig.update_layout(height=400, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True)
    except:
        st.error("Dữ liệu đang được tải...")

with tab_bctc:
    st.subheader(f"📊 Nội tạng Cá: {t_curr}")
    if not vietstock_db.empty:
        fish = vietstock_db[vietstock_db['Mã CK'] == t_curr]
        if not fish.empty:
            row = fish.iloc[0]
            c1, c2, c3 = st.columns(3)
            col_rev = quick_find_col("Doanh thu thuần")
            col_inv = quick_find_col("Hàng tồn kho")
            if col_rev: c1.metric("Doanh thu", f"{row[col_rev]/1e9:,.1f} Tỷ")
            if col_inv: c2.metric("Tồn kho", f"{row[col_inv]/1e9:,.1f} Tỷ")
            st.info("💡 Kiểm tra tồn kho tăng vọt là dấu hiệu SIÊU CÁ sắp bùng nổ!")