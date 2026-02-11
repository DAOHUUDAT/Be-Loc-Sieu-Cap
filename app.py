import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

# --- 1. THIẾT LẬP GIAO DIỆN ---
st.set_page_config(page_title="HÃY CHỌN CÁ ĐÚNG v6.3.6", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 1.6rem !important; font-weight: bold; color: #007bff; }
    section[data-testid="stSidebar"] { width: 310px !important; }
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
    st.header("📓 CẨM NANG")
    with st.expander("📖 Giải mã thông số", expanded=True):
        st.markdown("""
        - **🛡️ Niềm tin:** Sức khỏe nội tại.
        - **📊 Bar Chart:** Xanh (Doanh thu), Vàng (Lợi nhuận).
        - **🌡️ RSI:** Nhiệt độ dòng tiền.
        - **🍱 Thức ăn:** Dư địa tăng trưởng.
        """)

st.title("🚀 Bể Lọc v6.3.6: SIÊU CẤP VIP PRO")

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
    # (Giữ nguyên toàn bộ logic Radar v6.3.5)
    st.subheader("🤖 Top 20 Đệ Tử Cá")
    # ... [Đoạn mã Radar cũ] ...
    elite_20 = ["DGC", "MWG", "FPT", "TCB", "SSI", "HPG", "GVR", "CTR", "DBC", "VNM", "STB", "MBB", "ACB", "KBC", "VGC", "PVS", "PVD", "ANV", "VHC", "REE"]
    radar_list = []
    for tk in elite_20:
        try:
            d = yf.download(f"{tk}.VN", period="40d", progress=False)
            if not d.empty:
                if isinstance(d.columns, pd.MultiIndex): d.columns = d.columns.get_level_values(0)
                p_c = d['Close'].iloc[-1]
                v_now = d['Volume'].iloc[-1]; v_avg = d['Volume'].rolling(20).mean().iloc[-1]
                ma20 = d['Close'].rolling(20).mean().iloc[-1]
                radar_list.append({"Mã": tk, "Giá": f"{p_c:,.0f}", "Loại": "Cá Lớn 🐋" if p_c > ma20 and v_now > v_avg else "Cá Nhỏ 🐟", "Sóng": "🌊" if v_now > v_avg * 1.5 else "☕"})
        except: continue
    st.table(pd.DataFrame(radar_list))

with tab_analysis:
    try:
        t_obj = yf.Ticker(f"{t_input}.VN")
        s_df = t_obj.history(period="1y")
        if isinstance(s_df.columns, pd.MultiIndex): s_df.columns = s_df.columns.get_level_values(0)
        curr_p = float(s_df['Close'].iloc[-1])
        
        # Lấy dữ liệu tài chính cho biểu đồ 5 quý
        fin_q = t_obj.quarterly_financials
        
        # TÍNH NIỀM TIN
        try:
            rev_growth = ((fin_q.loc['Total Revenue'].iloc[0] / fin_q.loc['Total Revenue'].iloc[4]) - 1)
            trust = int(min(100, (rev_growth * 100) + (50 if curr_p > s_df['Close'].rolling(50).mean().iloc[-1] else 0)))
        except: rev_growth = 0.1; trust = 65

        # 1. Hiển thị Chỉ số & Định giá
        st.markdown(f"### 🛡️ Niềm tin {t_input}: {trust}%")
        c_p, c1, c2, c3 = st.columns(4)
        p_base = curr_p * (1 + rev_growth) * inf_factor
        c_p.metric("📍 GIÁ HIỆN TẠI", f"{curr_p:,.0f}")
        c1.metric("🐢 Thận trọng", f"{curr_p * (1 + rev_growth * 0.4) * inf_factor:,.0f}")
        c2.metric("🏠 Cơ sở", f"{p_base:,.0f}")
        c3.metric("🚀 Phi thường", f"{curr_p * (1 + rev_growth * 2) * inf_factor:,.0f}")

        # --- PHẦN MỚI: BIỂU ĐỒ TÀI CHÍNH 5 QUÝ ---
        st.subheader("📊 Sức khỏe tài chính 5 Quý gần nhất")
        if not fin_q.empty:
            # Lấy Doanh thu và Lợi nhuận ròng (Net Income)
            # Lưu ý: Một số mã có tên hàng khác nhau, dùng .get để tránh lỗi
            q_rev = fin_q.loc['Total Revenue'].iloc[:5][::-1] 
            try:
                q_net = fin_q.loc['Net Income'].iloc[:5][::-1]
            except:
                q_net = fin_q.loc['Net Income From Continuing Operation Net Extraordinaries'].iloc[:5][::-1]
            
            fig_fin = go.Figure()
            fig_fin.add_trace(go.Bar(x=q_rev.index.astype(str), y=q_rev, name='Doanh thu', marker_color='#007bff'))
            fig_fin.add_trace(go.Bar(x=q_net.index.astype(str), y=q_net, name='Lợi nhuận', marker_color='#FFD700'))
            fig_fin.update_layout(barmode='group', height=300, margin=dict(l=0,r=0,t=20,b=0), template="plotly_white")
            st.plotly_chart(fig_fin, use_container_width=True)
        else:
            st.warning("Không tìm thấy dữ liệu tài chính quý.")

        # --- 2. BIỂU ĐỒ KỸ THUẬT (GIỮ NGUYÊN TOÀN BỘ) ---
        st.subheader(f"📈 Phân tích kỹ thuật {t_input}")
        s_df['tk'] = (s_df['High'].rolling(9).max() + s_df['Low'].rolling(9).min())/2
        s_df['kj'] = (s_df['High'].rolling(26).max() + s_df['Low'].rolling(26).min())/2
        s_df['sa'] = ((s_df['tk'] + s_df['kj'])/2).shift(26)
        s_df['sb'] = ((s_df['High'].rolling(52).max() + s_df['Low'].rolling(52).min())/2).shift(26)
        s_df['Vol_Avg'] = s_df['Volume'].rolling(20).mean()
        
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.7, 0.3])
        fig.add_trace(go.Candlestick(x=s_df.index, open=s_df['Open'], high=s_df['High'], low=s_df['Low'], close=s_df['Close'], name='Giá'), row=1, col=1)
        fig.add_trace(go.Scatter(x=s_df.index, y=s_df['sa'], line=dict(width=0), showlegend=False), row=1, col=1)
        fig.add_trace(go.Scatter(x=s_df.index, y=s_df['sb'], line=dict(width=0), fill='tonexty', fillcolor='rgba(0, 150, 255, 0.1)', name='Mây'), row=1, col=1)
        fig.add_trace(go.Scatter(x=s_df.index, y=s_df['tk'], line=dict(color='#FF33CC', width=2), name='Tenkan'), row=1, col=1)
        fig.add_trace(go.Scatter(x=s_df.index, y=s_df['kj'], line=dict(color='#FFD700', width=2), name='Kijun'), row=1, col=1)
        
        v_colors = ['#FF4136' if s_df['Open'].iloc[i] > s_df['Close'].iloc[i] else '#2ECC40' for i in range(len(s_df))]
        fig.add_trace(go.Bar(x=s_df.index, y=s_df['Volume'], marker_color=v_colors, name='Vol'), row=2, col=1)
        fig.add_trace(go.Scatter(x=s_df.index, y=s_df['Vol_Avg'], line=dict(color='#39CCCC', width=1.5), name='Vol TB20'), row=2, col=1)
        
        fig.update_layout(height=500, xaxis_rangeslider_visible=False, template="plotly_white", margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True)

        if st.button(f"📌 Lưu {t_input} vào Sổ Vàng"):
            st.session_state.history_log.append({"Mã": t_input, "Giá": f"{curr_p:,.0f}", "Ngày": datetime.now().strftime("%d/%m")})
            st.rerun()
    except:
        st.error(f"Đang tầm soát mã cá {t_input}...")

with tab_history:
    if st.session_state.history_log:
        st.table(pd.DataFrame(st.session_state.history_log))
        if st.button("🗑️ Làm sạch sổ"):
            st.session_state.history_log = []
            st.rerun()
    else: st.info("Sổ vàng đang trống.")