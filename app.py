import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

# --- 1. CẤU HÌNH GIAO DIỆN SIÊU CẤP ---
st.set_page_config(page_title="HÃY CHỌN CÁ ĐÚNG v6.3.3", layout="wide")

st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 1.8rem !important; font-weight: bold; color: #007bff; }
    section[data-testid="stSidebar"] { width: 300px !important; }
    .stTable { border-radius: 12px; overflow: hidden; }
    </style>
    """, unsafe_allow_html=True)

if 'history_log' not in st.session_state: st.session_state['history_log'] = []

# --- HÀM TÍNH RSI (GIA VỊ MỚI) ---
def compute_rsi(data, window=14):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

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
        * **🌡️ RSI (Nhiệt độ):** > 70 (Nóng/Quá mua), < 30 (Lạnh/Quá bán).
        * **📊 Vol Avg:** Đường trắng so sánh khối lượng trung bình.
        * **🍱 Thức ăn:** Dư địa tăng trưởng kỳ vọng.
        * **✂️ ATR:** Điểm tựa quản trị rủi ro.
	* **🥇 ĐẠI CA (Score >=5):** Cá mập đã vào, thức ăn sạch, vị thế tốt.
	* **🥈 CẬN VỆ (Score 3-4):** Tiềm năng cao, đang tích lũy.
   	* **🥉 LÍNH MỚI (Score <3):** Đang tầm soát, chưa đủ xung lực.
	* **🌊 Sóng Ngầm:** Khối lượng vọt >150% trung bình 20 phiên.
    	* **📈 Định giá Co giãn:** Đã tính phí rủi ro thị trường (VN-Index).
        """)

st.title("🚀 Bể Lọc v6.3.4: FINAL PERFECTION")

# --- 3. TRẠM QUAN TRẮC ĐẠI DƯƠNG (BỌC THÉP CHỐNG TẮC ỐNG) ---
try:
    vni = yf.download("^VNI", period="150d", progress=False)
    if not vni.empty:
        if isinstance(vni.columns, pd.MultiIndex): vni.columns = vni.columns.get_level_values(0)
        v_c = float(vni['Close'].iloc[-1])
        vh26 = vni['High'].rolling(26).max(); vl26 = vni['Low'].rolling(26).min()
        vh9 = vni['High'].rolling(9).max(); vl9 = vni['Low'].rolling(9).min()
        vsa = (((vh9+vl9)/2 + (vh26+vl26)/2)/2).shift(26).iloc[-1]
        
        inf_factor = 1.1 if v_c > vsa else 0.9
        
        st.subheader(f"🌊 Đại Dương: {'🟢 THẢ LƯỚI' if v_c > vsa else '🔴 ĐÁNH KẺNG'}")
        c1, c2, c3 = st.columns(3)
        c1.metric("Chỉ số VN-Index", f"{v_c:.2f}")
        c2.info(f"Hệ số Co giãn Lạm phát: {inf_factor}x")
        c3.success("TRONG ẤM NGOÀI ÊM" if v_c > vsa else "CẢNH BÁO RỦI RO")
except: st.warning("📡 Vệ tinh đại dương đang kết nối lại... Hệ số mặc định: 1.0x")

# --- 4. HỆ THỐNG TABS ---
tab_radar, tab_analysis, tab_history = st.tabs(["🎯 RADAR", "💎 CHI TIẾT", "📓 SỔ VÀNG"])

with tab_radar:
    st.subheader("🤖 Radar Tầm Soát 20 Đệ Tử Cá")
elite_20 = [
    "DGC", "MWG", "FPT", "TCB", "SSI", "HPG", "GVR", "CTR", "DBC", "VNM",
    "STB", "MBB", "ACB", "KBC", "VGC", "PVS", "PVD", "ANV", "VHC", "REE"
]

radar_data = []
for ticker in elite_20:
    try:
        t_obj = yf.Ticker(f"{ticker}.VN")
        t_df = t_obj.history(period="60d")
        if isinstance(t_df.columns, pd.MultiIndex): t_df.columns = t_df.columns.get_level_values(0)
        
        # Sóng Ngầm
        v_now = t_df['Volume'].iloc[-1]; v_avg = t_df['Volume'].rolling(20).mean().iloc[-1]
        wave_score = 2 if v_now > v_avg * 1.5 else 0
        
        # Thức ăn sạch (G)
        fin = t_obj.quarterly_financials
        g_rate = ((fin.loc['Total Revenue'].iloc[0] / fin.loc['Total Revenue'].iloc[4]) - 1) * 100
        g_score = 3 if g_rate > 30 else (1 if g_rate > 0 else -1)
        
        # Vị thế Kumo
        h26_t = t_df['High'].rolling(26).max(); l26_t = t_df['Low'].rolling(26).min()
        vsa_t = (((t_df['High'].rolling(9).max()+t_df['Low'].rolling(9).min())/2 + (h26_t+l26_t)/2)/2).shift(26).iloc[-1]
        pos_score = 2 if t_df['Close'].iloc[-1] > vsa_t else 0
        
        total_score = wave_score + g_score + pos_score
        rank = "🥇 ĐẠI CA" if total_score >= 5 else ("🥈 CẬN VỆ" if total_score >= 3 else "🥉 LÍNH MỚI")
        
        radar_data.append({
            "Ưu tiên": rank, "Mã": ticker, "Điểm": total_score,
            "Sóng Ngầm": "🌊 MẠNH" if wave_score > 0 else "Yên ắng",
            "Thức ăn (G)": f"{g_rate:.1f}%", "Giá Hiện Tại": f"{t_df['Close'].iloc[-1]:,.0f}"
        })
    except: continue
    st.table(pd.DataFrame(radar_list))

with tab_analysis:
    try:
        t_obj = yf.Ticker(f"{t_input}.VN")
        s_df = t_obj.history(period="1y")
        if isinstance(s_df.columns, pd.MultiIndex): s_df.columns = s_df.columns.get_level_values(0)
        curr_p = s_df['Close'].iloc[-1]
        
        # TÍNH RSI & VOL AVG
        s_df['RSI'] = compute_rsi(s_df['Close'])
        s_df['Vol_Avg'] = s_df['Volume'].rolling(20).mean()
        curr_rsi = s_df['RSI'].iloc[-1]
        
        # --- NIỀM TIN & ĐỊNH GIÁ ---
        try:
            fin = t_obj.quarterly_financials
            rev_g = (fin.loc['Total Revenue'].iloc[0] / fin.loc['Total Revenue'].iloc[4] - 1)
            trust = int(min(100, (rev_g * 100) + (50 if curr_p > s_df['Close'].rolling(50).mean().iloc[-1] else 0)))
        except: rev_g = 0.1; trust = 65

        # Hiển thị RSI
        rsi_color = "red" if curr_rsi > 70 else "green" if curr_rsi < 30 else "orange"
        st.markdown(f"🛡️ Niềm tin: **{trust}%** | 🌡️ Nhiệt độ RSI: <span style='color:{rsi_color}'>**{curr_rsi:.1f}**</span>", unsafe_allow_html=True)
        st.progress(max(0, min(trust / 100, 1.0)))

        c1, c2, c3 = st.columns(3)
        p_than_trong = curr_p * (1 + rev_g * 0.4) * inf_factor
        p_co_so = curr_p * (1 + rev_g) * inf_factor
        p_phi_thuong = curr_p * (1 + rev_g * 2) * inf_factor
        
        c1.metric("🐢 Thận trọng", f"{p_than_trong:,.0f}")
        c2.metric("🏠 Cơ sở", f"{p_co_so:,.0f}")
        c3.metric("🚀 Phi thường", f"{p_phi_thuong:,.0f}")

        # --- BIỂU ĐỒ SUBPLOTS (NẾN + VOL) ---
        h9 = s_df['High'].rolling(9).max(); l9 = s_df['Low'].rolling(9).min(); s_df['tk'] = (h9+l9)/2
        h26 = s_df['High'].rolling(26).max(); l26 = s_df['Low'].rolling(26).min(); s_df['kj'] = (h26+l26)/2
        s_df['sa'] = ((s_df['tk'] + s_df['kj'])/2).shift(26)
        s_df['sb'] = ((s_df['High'].rolling(52).max() + s_df['Low'].rolling(52).min())/2).shift(26)
        
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.7, 0.3])
        
        # Row 1: Giá & Ichimoku
        fig.add_trace(go.Scatter(x=s_df.index, y=s_df['sa'], line=dict(width=0), showlegend=False), row=1, col=1)
        fig.add_trace(go.Scatter(x=s_df.index, y=s_df['sb'], line=dict(width=0), fill='tonexty', fillcolor='rgba(0, 150, 255, 0.1)', name='Mây'), row=1, col=1)
        fig.add_trace(go.Candlestick(x=s_df.index, open=s_df['Open'], high=s_df['High'], low=s_df['Low'], close=s_df['Close'], name='Giá'), row=1, col=1)
        fig.add_trace(go.Scatter(x=s_df.index, y=s_df['tk'], line=dict(color='#FF33CC', width=2), name='Tenkan'), row=1, col=1)
        fig.add_trace(go.Scatter(x=s_df.index, y=s_df['kj'], line=dict(color='#FFD700', width=2), name='Kijun'), row=1, col=1)
        
        # Thêm nhãn định giá Cơ sở trực tiếp lên chart
        fig.add_hline(y=p_co_so, line_dash="dot", line_color="orange", annotation_text="ĐỊNH GIÁ CS", row=1, col=1)

        # Row 2: Volume & Vol Avg
        vol_colors = ['#FF4136' if s_df['Open'].iloc[i] > s_df['Close'].iloc[i] else '#2ECC40' for i in range(len(s_df))]
        fig.add_trace(go.Bar(x=s_df.index, y=s_df['Volume'], name='Vol', marker_color=vol_colors), row=2, col=1)
        fig.add_trace(go.Scatter(x=s_df.index, y=s_df['Vol_Avg'], line=dict(color='#39CCCC', width=1.5), name='Vol TB20'), row=2, col=1)
        
        fig.update_layout(height=650, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False, template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)

        if st.button(f"📌 Ghi vào Sổ Vàng"):
            st.session_state.history_log.append({"Mã": t_input, "Giá": f"{curr_p:,.0f}", "Ngày": datetime.now().strftime("%d/%m")})
            st.rerun()
    except: st.error("Mã cá đang ẩn mình, hãy thử lại.")

with tab_history:
    if st.session_state.history_log:
        st.table(pd.DataFrame(st.session_state.history_log))
        if st.button("🗑️ Xóa hết"):
            st.session_state.history_log = []
            st.rerun()
    else: st.info("Sổ vàng đang trống.")