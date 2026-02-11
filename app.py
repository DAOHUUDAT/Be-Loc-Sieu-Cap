import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

# --- 1. THIẾT LẬP HỆ THỐNG (Hàn ống giao diện) ---
st.set_page_config(page_title="HÃY CHỌN CÁ ĐÚNG v6.3.3", layout="wide")

st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 1.8rem !important; font-weight: bold; color: #007bff; }
    section[data-testid="stSidebar"] { width: 300px !important; }
    .stTable { border-radius: 12px; overflow: hidden; }
    </style>
    """, unsafe_allow_html=True)

if 'history_log' not in st.session_state: 
    st.session_state['history_log'] = [] # Khởi tạo sổ vàng 

# --- HÀM TÍNH TOÁN LÕI ---
def compute_rsi(data, window=14):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# --- 2. SIDEBAR: TRI KỶ & CẨM NANG NÂNG CẤP ---
with st.sidebar:
    try:
        # Chèn ảnh tri kỷ vào sidebar theo yêu cầu từ v6.1
        st.image("https://raw.githubusercontent.com/daohuudat/be-loc-sieu-cap/main/tri-ky.jpg", use_container_width=True)
    except:
        st.info("🖼️ [Đang nạp ảnh tri kỷ...]")
    
    st.header("🎮 ĐÀI CHỈ HUY")
    t_input = st.text_input("🔍 SOI MÃ CÁ", "VGC").upper()
    st.divider()
    
    st.header("📓 CẨM NANG CHIẾN THUẬT")
    with st.expander("📖 Giải mã thông số", expanded=True):
        st.markdown("""
        - **🛡️ Niềm tin > 80%:** Cá Lớn thực thụ[cite: 19].
        - **🌊 Sóng:** Mạnh khi Vol > 150% TB 20 phiên[cite: 19].
        - **🌡️ RSI:** >70 (Nóng), <30 (Lạnh).
        - **🍱 Thức ăn:** Dư địa % về giá cơ sở/MA20.
        - **✂️ ATR:** Điểm tựa quản trị rủi ro[cite: 19].
        """)

st.title("🚀 Bể Lọc v6.3.3: FINAL PERFECTION")

# --- 3. TRẠM QUAN TRẮC ĐẠI DƯƠNG (Hệ số co giãn VNI) ---
inf_factor = 1.0 
try:
    vni = yf.download("^VNI", period="150d", progress=False)
    if not vni.empty:
        if isinstance(vni.columns, pd.MultiIndex): vni.columns = vni.columns.get_level_values(0)
        v_c = float(vni['Close'].iloc[-1])
        # Thuật toán Ichimoku cho VNI [cite: 22]
        vh26 = vni['High'].rolling(26).max(); vl26 = vni['Low'].rolling(26).min()
        vh9 = vni['High'].rolling(9).max(); vl9 = vni['Low'].rolling(9).min()
        vsa = (((vh9+vl9)/2 + (vh26+vl26)/2)/2).shift(26).iloc[-1]
        
        # Hệ số an toàn co giãn 
        inf_factor = 1.15 if v_c > vsa else 0.85
        st.info(f"🌊 Đại Dương: {'🟢 THẢ LƯỚI (Sóng Thuận)' if v_c > vsa else '🔴 ĐÁNH KẺNG (Sóng Nghịch)'} | Hệ số co giãn: {inf_factor}x")
except: pass

# --- 4. HỆ THỐNG TABS TINH CHỈNH ---
tab_radar, tab_analysis, tab_history = st.tabs(["🎯 RADAR ELITE", "💎 CHI TIẾT SIÊU CÁ", "📓 SỔ VÀNG"])

with tab_radar:
    st.subheader("🤖 Top 20 Đệ Tử Cá (Tầm soát đa tầng)")
    elite_20 = ["DGC", "MWG", "FPT", "TCB", "SSI", "HPG", "GVR", "CTR", "DBC", "VNM", "STB", "MBB", "ACB", "KBC", "VGC", "PVS", "PVD", "ANV", "VHC", "REE"]
    radar_list = []
    
    with st.spinner('Đang đo nhiệt độ nước...'):
        for tk in elite_20:
            try:
                d = yf.download(f"{tk}.VN", period="50d", progress=False)
                if not d.empty:
                    if isinstance(d.columns, pd.MultiIndex): d.columns = d.columns.get_level_values(0)
                    p_c = d['Close'].iloc[-1]
                    v_now = d['Volume'].iloc[-1]; v_avg = d['Volume'].rolling(20).mean().iloc[-1]
                    ma20 = d['Close'].rolling(20).mean().iloc[-1]
                    
                    # Tính RSI cho Radar
                    d['RSI'] = compute_rsi(d['Close'])
                    curr_rsi = d['RSI'].iloc[-1]
                    
                    # Phân loại cá dựa trên điểm số 
                    is_big = p_c > ma20 and v_now > v_avg
                    loai = "Cá Lớn 🐋" if is_big else "Cá Nhỏ 🐟"
                    temp = "🔥 Nóng" if curr_rsi > 70 else "❄️ Lạnh" if curr_rsi < 30 else "🌤️ Êm"
                    
                    radar_list.append({
                        "Mã": tk, "Giá": f"{p_c:,.0f}",
                        "Sóng": "🌊 Mạnh" if v_now > v_avg * 1.5 else "☕ Lặng",
                        "Nhiệt độ": temp, "RSI": round(curr_rsi, 1),
                        "Loại": loai,
                        "Thức ăn": f"{((ma20/p_c)-1)*100:+.1f}%" if not is_big else "✅ Đủ đầy"
                    })
            except: continue
    st.table(pd.DataFrame(radar_list))

with tab_analysis:
    try:
        t_obj = yf.Ticker(f"{t_input}.VN")
        s_df = t_obj.history(period="1y") # Lấy 1 năm dữ liệu [cite: 29]
        if isinstance(s_df.columns, pd.MultiIndex): s_df.columns = s_df.columns.get_level_values(0)
        curr_p = float(s_df['Close'].iloc[-1])
        
        # 1. Tấm lọc RSI & Volume Average
        s_df['RSI'] = compute_rsi(s_df['Close'])
        s_df['Vol_Avg'] = s_df['Volume'].rolling(20).mean()
        curr_rsi = s_df['RSI'].iloc[-1]
        
        # 2. Ma trận Niềm tin & Định giá (Hàn từ v5.5) [cite: 30]
        try:
            fin = t_obj.quarterly_financials
            g_val = ((fin.loc['Total Revenue'].iloc[0] / fin.loc['Total Revenue'].iloc[4]) - 1)
            trust = int(min(100, (g_val * 100) + (50 if curr_p > s_df['Close'].rolling(50).mean().iloc[-1] else 0)))
        except: g_val = 0.1; trust = 65

        st.markdown(f"### 🛡️ Niềm tin {t_input}: {trust}% | RSI: {curr_rsi:.1f}")
        st.progress(max(0, min(trust / 100, 1.0)))

        m1, m2, m3 = st.columns(3)
        p_base = curr_p * (1 + g_val) * inf_factor
        m1.metric("🐢 Thận trọng", f"{curr_p * (1 + g_val * 0.4) * inf_factor:,.0f}")
        m2.metric("🏠 Cơ sở (Target)", f"{p_base:,.0f}")
        m3.metric("🚀 Phi thường", f"{curr_p * (1 + g_val * 2) * inf_factor:,.0f}")

        # 3. Biểu đồ Ichimoku & Volume (Gia vị mobile)
        # Tính toán Ichimoku [cite: 31, 32]
        s_df['tk'] = (s_df['High'].rolling(9).max() + s_df['Low'].rolling(9).min())/2
        s_df['kj'] = (s_df['High'].rolling(26).max() + s_df['Low'].rolling(26).min())/2
        s_df['sa'] = ((s_df['tk'] + s_df['kj'])/2).shift(26)
        s_df['sb'] = ((s_df['High'].rolling(52).max() + s_df['Low'].rolling(52).min())/2).shift(26)
        
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.7, 0.3])
        
        # Nến & Mây Ichimoku
        fig.add_trace(go.Candlestick(x=s_df.index, open=s_df['Open'], high=s_df['High'], low=s_df['Low'], close=s_df['Close'], name='Giá'), row=1, col=1)
        fig.add_trace(go.Scatter(x=s_df.index, y=s_df['sa'], line=dict(width=0), showlegend=False), row=1, col=1)
        fig.add_trace(go.Scatter(x=s_df.index, y=s_df['sb'], line=dict(width=0), fill='tonexty', fillcolor='rgba(0, 150, 255, 0.1)', name='Mây'), row=1, col=1)
        
        # Đường định giá cơ sở trực tiếp lên chart
        fig.add_hline(y=p_base, line_dash="dot", line_color="orange", annotation_text="TARGET CƠ SỞ", row=1, col=1)

        # Volume rực rỡ & Đường trung bình 20 phiên
        colors = ['#FF4136' if s_df['Open'].iloc[i] > s_df['Close'].iloc[i] else '#2ECC40' for i in range(len(s_df))]
        fig.add_trace(go.Bar(x=s_df.index, y=s_df['Volume'], marker_color=colors, name='Volume'), row=2, col=1)
        fig.add_trace(go.Scatter(x=s_df.index, y=s_df['Vol_Avg'], line=dict(color='#39CCCC', width=1.5), name='Vol TB20'), row=2, col=1)
        
        fig.update_layout(height=600, xaxis_rangeslider_visible=False, template="plotly_white", margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True)

        if st.button(f"📌 Lưu {t_input} vào Sổ Vàng"):
            st.session_state.history_log.append({"Mã": t_input, "Giá": f"{curr_p:,.0f}", "Ngày": datetime.now().strftime("%d/%m")})
            st.rerun()
    except Exception as e:
        st.error(f"Đang tầm soát mã cá {t_input}...")

with tab_history:
    st.subheader("📓 Sổ Vàng Cá Lớn")
    if st.session_state.history_log: # Sửa lỗi traceback ảnh 13 
        st.table(pd.DataFrame(st.session_state.history_log))
        if st.button("🗑️ Làm sạch sổ"):
            st.session_state.history_log = []
            st.rerun()
    else:
        st.info("Sổ vàng đang đợi những con cá lớn...")