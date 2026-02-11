import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

# --- 1. CẤU HÌNH GIAO DIỆN SIÊU CẤP ---
st.set_page_config(page_title="HÃY CHỌN CÁ ĐÚNG v6.3.2", layout="wide")

st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 1.8rem !important; font-weight: bold; color: #007bff; }
    section[data-testid="stSidebar"] { width: 300px !important; }
    .stTable { border-radius: 12px; overflow: hidden; }
    </style>
    """, unsafe_allow_html=True)

if 'history_log' not in st.session_state: st.session_state['history_log'] = []

# --- 2. SIDEBAR: ẢNH TRI KỶ & CẨM NANG NÂNG CẤP ---
with st.sidebar:
    try:
        st.image("https://raw.githubusercontent.com/daohuudat/be-loc-sieu-cap/main/tri-ky.jpg", use_container_width=True)
    except:
        st.info("🖼️ [Đang nạp ảnh tri kỷ...]")
    
    st.header("🎮 ĐÀI CHỈ HUY")
    t_input = st.text_input("🔍 SOI MÃ CÁ", "VGC").upper()
    st.divider()
    
    st.header("📓 CẨM NANG")
    with st.expander("📖 Giải mã thông số", expanded=True):
        st.markdown("""
        * **🛡️ Niềm tin > 80%:** Cá Lớn thực thụ.
        * **🌊 Giải mã Sóng:**
            - *Sóng Lớn:* Dòng tiền Cá Mập vào mạnh (Vol > 150%).
            - *Sóng Lặng:* Tích lũy, chờ đợi thời cơ.
        * **📊 Volume:** Xanh (Cầu mạnh), Đỏ (Cung xả).
        * **🍱 Thức ăn:** Dư địa tăng trưởng dựa trên định giá Ma trận.
        * **✂️ ATR:** Điểm tựa quản trị rủi ro.
        """)

st.title("🚀 Bể Lọc v6.3.2: SIÊU CẤP VIP PRO")

# --- 3. TRẠM QUAN TRẮC ĐẠI DƯƠNG ---
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
        st.info(f"🌊 Đại Dương: {'🟢 THẢ LƯỚI (Sóng Thuận)' if v_c > v_sa else '🔴 ĐÁNH KẺNG (Sóng Nghịch)'}")
except: pass

# --- 4. HỆ THỐNG TABS ---
tab_radar, tab_analysis, tab_history = st.tabs(["🎯 RADAR", "💎 CHI TIẾT", "📓 SỔ VÀNG"])

with tab_radar:
    st.subheader("🤖 Top 20 Đệ Tử Cá (Kèm Thức Ăn)")
    elite_20 = ["DGC", "MWG", "FPT", "TCB", "SSI", "HPG", "GVR", "CTR", "DBC", "VNM", "STB", "MBB", "ACB", "KBC", "VGC", "PVS", "PVD", "ANV", "VHC", "REE"]
    radar_list = []
    
    with st.spinner('Đang tầm soát thực phẩm...'):
        for tk in elite_20:
            try:
                d = yf.download(f"{tk}.VN", period="40d", progress=False)
                if not d.empty:
                    if isinstance(d.columns, pd.MultiIndex): d.columns = d.columns.get_level_values(0)
                    v_now = d['Volume'].iloc[-1]; v_avg = d['Volume'].rolling(20).mean().iloc[-1]
                    p_c = d['Close'].iloc[-1]
                    ma20 = d['Close'].rolling(20).mean().iloc[-1]
                    
                    loai = "Cá Lớn 🐋" if p_c > ma20 and v_now > v_avg else "Cá Nhỏ 🐟"
                    # Tính "Thức ăn" - Tạm tính dư địa lên MA20 (Hoặc định giá nhanh)
                    thuc_an = f"{((ma20/p_c)-1)*100:+.1f}%" if p_c < ma20 else "Đang no"
                    
                    radar_list.append({
                        "Mã": tk, "Giá": f"{p_c:,.0f}",
                        "Sóng": "🌊 Lớn" if v_now > v_avg * 1.5 else "☕ Lặng",
                        "Loại": loai,
                        "Thức Ăn": thuc_an,
                        "Lệnh": "MUA/GIỮ" if loai == "Cá Lớn 🐋" else "QUAN SÁT"
                    })
            except: continue
    st.table(pd.DataFrame(radar_list))

with tab_analysis:
    try:
        t_obj = yf.Ticker(f"{t_input}.VN")
        s_df = t_obj.history(period="1y")
        if isinstance(s_df.columns, pd.MultiIndex): s_df.columns = s_df.columns.get_level_values(0)
        curr_p = s_df['Close'].iloc[-1]
        
        # --- NIỀM TIN & ĐỊNH GIÁ (GIỮ NGUYÊN ỐNG) ---
        try:
            fin = t_obj.quarterly_financials
            rev_g = (fin.loc['Total Revenue'].iloc[0] / fin.loc['Total Revenue'].iloc[4] - 1)
            trust = int(min(100, (rev_g * 100) + (50 if curr_p > s_df['Close'].rolling(50).mean().iloc[-1] else 0)))
        except: rev_g = 0.1; trust = 65

        st.subheader(f"🛡️ Niềm tin {t_input}: {trust}%")
        st.progress(max(0, min(trust / 100, 1.0)))

        c1, c2, c3 = st.columns(3)
        c1.metric("🐢 Thận trọng", f"{curr_p * (1 + rev_g * 0.4) * inf_factor:,.0f}")
        c2.metric("🏠 Cơ sở", f"{curr_p * (1 + rev_g) * inf_factor:,.0f}")
        c3.metric("🚀 Phi thường", f"{curr_p * (1 + rev_g * 2) * inf_factor:,.0f}")

        # --- ICHIMOKU + VOLUME (FULL GIA VỊ) ---
        h9 = s_df['High'].rolling(9).max(); l9 = s_df['Low'].rolling(9).min(); s_df['tk'] = (h9+l9)/2
        h26 = s_df['High'].rolling(26).max(); l26 = s_df['Low'].rolling(26).min(); s_df['kj'] = (h26+l26)/2
        s_df['sa'] = ((s_df['tk'] + s_df['kj'])/2).shift(26)
        s_df['sb'] = ((s_df['High'].rolling(52).max() + s_df['Low'].rolling(52).min())/2).shift(26)
        
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.7, 0.3])
        fig.add_trace(go.Scatter(x=s_df.index, y=s_df['sa'], line=dict(width=0), showlegend=False), row=1, col=1)
        fig.add_trace(go.Scatter(x=s_df.index, y=s_df['sb'], line=dict(width=0), fill='tonexty', fillcolor='rgba(0, 150, 255, 0.15)', name='Mây'), row=1, col=1)
        fig.add_trace(go.Candlestick(x=s_df.index, open=s_df['Open'], high=s_df['High'], low=s_df['Low'], close=s_df['Close'], name='Giá'), row=1, col=1)
        fig.add_trace(go.Scatter(x=s_df.index, y=s_df['tk'], line=dict(color='#FF33CC', width=2), name='Tenkan'), row=1, col=1)
        fig.add_trace(go.Scatter(x=s_df.index, y=s_df['kj'], line=dict(color='#FFD700', width=2), name='Kijun'), row=1, col=1)

        # Cột Volume với màu sắc rực rỡ cho Mobile
        vol_colors = ['#FF4136' if s_df['Open'].iloc[i] > s_df['Close'].iloc[i] else '#2ECC40' for i in range(len(s_df))]
        fig.add_trace(go.Bar(x=s_df.index, y=s_df['Volume'], name='Khối lượng', marker_color=vol_colors), row=2, col=1)
        
        fig.update_layout(height=600, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False, template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)

        if st.button(f"📌 Ghi vào Sổ Vàng"):
            st.session_state.history_log.append({"Mã": t_input, "Giá": f"{curr_p:,.0f}", "Ngày": datetime.now().strftime("%d/%m")})
            st.rerun()
    except: st.error("Mã cá đang lặn, hãy thử mã khác.")

with tab_history:
    st.subheader("📓 Nhật ký Sổ Vàng")
    if st.session_state.history_log:
        st.table(pd.DataFrame(st.session_state.history_log))
        if st.button("🗑️ Xóa hết"):
            st.session_state.history_log = []
            st.rerun()
    else:
        st.info("Sổ vàng đang đợi những con cá lớn...")