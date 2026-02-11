import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- 1. CẤU HÌNH GIAO DIỆN SIÊU CẤP ---
st.set_page_config(page_title="HÃY CHỌN CÁ ĐÚNG v6.2.1", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .main { background-color: transparent; }
    [data-testid="stMetricValue"] { font-size: 1.8rem !important; font-weight: bold; color: #007bff; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { border-radius: 8px; padding: 10px; font-weight: bold; }
    .stDataFrame { border: 1px solid #444; border-radius: 12px; }
    </style>
    """, unsafe_allow_html=True)

if 'history_log' not in st.session_state: st.session_state['history_log'] = []

# --- 2. SIDEBAR (CẨM NANG VÀ ĐIỀU KHIỂN) ---
with st.sidebar:
    st.header("🎮 ĐÀI CHỈ HUY")
    t_input = st.text_input("🔍 SOI MÃ CÁ", "VGC").upper()
    st.divider()
    st.header("📓 CẨM NANG")
    with st.expander("📖 Giải mã thông số", expanded=True):
        st.markdown("""
        * **🛡️ Niềm tin > 80%:** Cá Lớn thực thụ.
        * **🌊 Sóng Ngầm:** Vol > 150%.
        * **📈 Co giãn:** Theo nhiệt độ Index.
        * **✂️ ATR:** Điểm cắt lỗ (2x), Chốt lời (3x).
        """)

st.title("🔱 HÃY CHỌN CÁ ĐÚNG v6.2.1")

# --- 3. TRẠM QUAN TRẮC ĐẠI DƯƠNG (VNI) ---
inf_factor = 1.0
try:
    vni = yf.download("^VNI", period="150d", progress=False)
    if not vni.empty:
        if isinstance(vni.columns, pd.MultiIndex): vni.columns = vni.columns.get_level_values(0)
        v_c = vni['Close'].iloc[-1]
        v_h26 = vni['High'].rolling(26).max(); v_l26 = vni['Low'].rolling(26).min()
        v_h9 = vni['High'].rolling(9).max(); v_l9 = vni['Low'].rolling(9).min()
        v_sa = (((v_h9+v_l9)/2 + (v_h26+v_l26)/2)/2).shift(26).iloc[-1]
        inf_factor = 1.15 if v_c > v_sa else 0.85
        st.info(f"🌊 Đại Dương: {'🟢 THẢ LƯỚI' if v_c > v_sa else '🔴 ĐÁNH KẺNG'}")
except: pass

# --- 4. HỆ THỐNG TABS ---
tab_radar, tab_analysis, tab_history = st.tabs(["🎯 RADAR", "💎 CHI TIẾT", "📓 SỔ VÀNG"])

with tab_radar:
    # ẢNH TRI KỶ (Đã gia cố hiển thị)
    try:
        st.image("https://raw.githubusercontent.com/DAOHUUDAT/Be-Loc-Sieu-Cap/refs/heads/main/anh-tri-ky.jpg", 
                 caption="AI Invest Partnership - Đồng hành tầm soát cá lớn", use_container_width=True)
    except: st.write("🖼️ [Hệ thống đang nạp ảnh tri kỷ...]")

    st.subheader("🤖 Top 20 Đệ Tử Cá")
    elite_20 = ["DGC", "MWG", "FPT", "TCB", "SSI", "HPG", "GVR", "CTR", "DBC", "VNM", "STB", "MBB", "ACB", "KBC", "VGC", "PVS", "PVD", "ANV", "VHC", "REE"]
    radar_data = []
    with st.spinner('Đang quét biển...'):
        for tk in elite_20:
            try:
                d = yf.download(f"{tk}.VN", period="20d", progress=False)
                if not d.empty:
                    if isinstance(d.columns, pd.MultiIndex): d.columns = d.columns.get_level_values(0)
                    v_now = d['Volume'].iloc[-1]; v_avg = d['Volume'].mean()
                    radar_data.append({"Mã": tk, "Score": 3 if v_now > v_avg*1.5 else 1, "Giá": f"{d['Close'].iloc[-1]:,.0f}"})
            except: continue
    st.dataframe(pd.DataFrame(radar_data).sort_values("Score", ascending=False), use_container_width=True, hide_index=True)

with tab_analysis:
    try:
        t_obj = yf.Ticker(f"{t_input}.VN")
        s_df = t_obj.history(period="1y")
        if isinstance(s_df.columns, pd.MultiIndex): s_df.columns = s_df.columns.get_level_values(0)
        curr_p = s_df['Close'].iloc[-1]
        
        # --- TẦM SOÁT NIỀM TIN (Hàn chuẩn ống v5.5.1) ---
        try:
            fin = t_obj.quarterly_financials
            rev_g = (fin.loc['Total Revenue'].iloc[0] / fin.loc['Total Revenue'].iloc[4] - 1)
            trust_score = int(min(100, (rev_g * 100) + (50 if curr_p > s_df['Close'].rolling(50).mean().iloc[-1] else 0)))
        except: 
            rev_g = 0.1; trust_score = 65

        st.subheader(f"🛡️ Niềm tin {t_input}: {trust_score}%")
        st.progress(max(0, min(trust_score / 100, 1.0)))

        # Định giá 3 kịch bản
        c1, c2, c3 = st.columns(3)
        c1.metric("🐢 Thận trọng", f"{curr_p * (1 + rev_g * 0.4) * inf_factor:,.0f}")
        c2.metric("🏠 Cơ sở", f"{curr_p * (1 + rev_g) * inf_factor:,.0f}")
        c3.metric("🚀 Phi thường", f"{curr_p * (1 + rev_g * 2) * inf_factor:,.0f}")

        # --- ICHIMOKU & ATR (Đã tối ưu màu sắc) ---
        s_df['ATR'] = pd.concat([(s_df['High']-s_df['Low']), (s_df['High']-s_df['Close'].shift()).abs(), (s_df['Low']-s_df['Close'].shift()).abs()], axis=1).max(axis=1).rolling(14).mean()
        h9 = s_df['High'].rolling(9).max(); l9 = s_df['Low'].rolling(9).min(); s_df['tk'] = (h9+l9)/2
        h26 = s_df['High'].rolling(26).max(); l26 = s_df['Low'].rolling(26).min(); s_df['kj'] = (h26+l26)/2
        s_df['sa'] = ((s_df['tk'] + s_df['kj'])/2).shift(26)
        s_df['sb'] = ((s_df['High'].rolling(52).max() + s_df['Low'].rolling(52).min())/2).shift(26)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=s_df.index, y=s_df['sa'], line=dict(width=0), showlegend=False))
        fig.add_trace(go.Scatter(x=s_df.index, y=s_df['sb'], line=dict(width=0), fill='tonexty', fillcolor='rgba(0, 150, 255, 0.15)', name='Mây Kumo'))
        fig.add_trace(go.Candlestick(x=s_df.index, open=s_df['Open'], high=s_df['High'], low=s_df['Low'], close=s_df['Close'], name='Giá'))
        fig.add_trace(go.Scatter(x=s_df.index, y=s_df['tk'], line=dict(color='#FF33CC', width=2), name='Tenkan'))
        fig.add_trace(go.Scatter(x=s_df.index, y=s_df['kj'], line=dict(color='#FFD700', width=2.5), name='Kijun'))
        
        atr_v = float(s_df['ATR'].iloc[-1])
        fig.add_hline(y=curr_p + (3*atr_v), line_dash="dash", line_color="#00ffff", annotation_text="TARGET")
        fig.add_hline(y=curr_p - (2*atr_v), line_dash="dash", line_color="#ff4444", annotation_text="CUT LOSS")
        
        fig.update_layout(height=500, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False, template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)

        if st.button(f"📌 Lưu {t_input}"):
            st.session_state.history_log.append({"Mã": t_input, "Giá": f"{curr_p:,.0f}", "Ngày": datetime.now().strftime("%d/%m")})
            st.rerun()
    except: st.error("Mã cá này đang lặn quá sâu, hãy thử mã khác!")

with tab_history:
    st.subheader("📓 Nhật ký Sổ Vàng")
    if st.session_state.history_log:
        st.table(pd.DataFrame(st.session_state.history_log))
        if st.button("🗑️ Xóa lịch sử"):
            st.session_state.history_log = []
            st.rerun()
    else: st.info("Chưa có ghi chép nào.")