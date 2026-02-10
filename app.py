import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- 1. CẤU HÌNH GIAO DIỆN SÁNG (Dễ nhìn trên Mobile) ---
st.set_page_config(page_title="HÃY CHỌN CÁ ĐÚNG v5.9.1", layout="wide")

# Khử nền đen khó nhìn, dùng màu nền sáng và chữ đậm rõ nét
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; color: #1e1e1e; }
    [data-testid="stMetricValue"] { font-size: 1.6rem !important; color: #007bff !important; font-weight: bold; }
    .stTabs [data-baseweb="tab-list"] { background-color: #ffffff; border-radius: 10px; padding: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
    .stTabs [data-baseweb="tab"] { color: #444; font-weight: 600; }
    .stTabs [data-baseweb="tab--active"] { color: #007bff !important; border-bottom: 2px solid #007bff; }
    .stExpander { background-color: #ffffff !important; border: 1px solid #dee2e6 !important; border-radius: 10px !important; }
    .sidebar .sidebar-content { background-color: #ffffff; }
    </style>
    """, unsafe_allow_html=True)

if 'history_log' not in st.session_state: st.session_state['history_log'] = []

# --- 2. SIDEBAR: CẨM NANG & ĐIỀU KHIỂN (Giữ nguyên gia sản) ---
with st.sidebar:
    st.header("🎮 ĐÀI CHỈ HUY")
    t_input = st.text_input("🔍 SOI MÃ CÁ", "VGC").upper()
    st.divider()
    st.header("📓 CẨM NANG CÂU CÁ")
    with st.expander("📖 Giải mã thông số", expanded=True):
        st.markdown("""
        * **🛡️ Niềm tin > 80%:** Cá Siêu cấp.
        * **🌊 Sóng Ngầm:** Vol > 150%.
        * **🥇 ĐẠI CA:** Dẫn đầu Elite 20.
        * **📈 Co giãn:** Theo nhiệt độ VNI.
        * **✂️ ATR:** Cắt lỗ kỷ luật.
        """)

st.title("🔱 HÃY CHỌN CÁ ĐÚNG v5.9.1")

# --- 3. TRẠM QUAN TRẮC ĐẠI DƯƠNG (Full ống dẫn) ---
try:
    vni = yf.download("^VNI", period="150d", progress=False)
    if not vni.empty:
        if isinstance(vni.columns, pd.MultiIndex): vni.columns = vni.columns.get_level_values(0)
        v_c = float(vni['Close'].iloc[-1])
        vh26_v = vni['High'].rolling(26).max(); vl26_v = vni['Low'].rolling(26).min()
        vh9_v = vni['High'].rolling(9).max(); vl9_v = vni['Low'].rolling(9).min()
        vsa = (((vh9_v+vl9_v)/2 + (vh26_v+vl26_v)/2)/2).shift(26).iloc[-1]
        inf_factor = 1.1 if v_c > vsa else 0.85
        
        st.info(f"🌊 **Đại Dương:** {'🟢 THẢ LƯỚI' if v_c > vsa else '🔴 ĐÁNH KẺNG'}")
        c1, c2 = st.columns(2)
        c1.metric("VN-Index", f"{v_c:.1f}")
        c2.metric("Hệ số Co giãn", f"{inf_factor}x")
except: st.warning("Đang kết nối vệ tinh...")

# --- 4. HỆ THỐNG TABS PHÂN LỚP ---
tab_radar, tab_analysis, tab_history = st.tabs(["🎯 RADAR ELITE", "💎 SOI CHI TIẾT", "📓 SỔ VÀNG"])

with tab_radar:
    st.subheader("🤖 Top 20 Đệ Tử Cá")
    elite_20 = ["DGC", "MWG", "FPT", "TCB", "SSI", "HPG", "GVR", "CTR", "DBC", "VNM", "STB", "MBB", "ACB", "KBC", "VGC", "PVS", "PVD", "ANV", "VHC", "REE"]
    radar_data = []
    with st.spinner('Đang quét biển...'):
        for ticker in elite_20:
            try:
                t_obj = yf.Ticker(f"{ticker}.VN")
                t_df = t_obj.history(period="60d")
                if isinstance(t_df.columns, pd.MultiIndex): t_df.columns = t_df.columns.get_level_values(0)
                v_now = t_df['Volume'].iloc[-1]; v_avg = t_df['Volume'].rolling(20).mean().iloc[-1]
                fin = t_obj.quarterly_financials
                g_rate = ((fin.loc['Total Revenue'].iloc[0] / fin.loc['Total Revenue'].iloc[4]) - 1) * 100
                score = (2 if v_now > v_avg * 1.5 else 0) + (3 if g_rate > 25 else 1)
                radar_data.append({"Hạng": "🥇" if score >= 4 else "🥈", "Mã": ticker, "Điểm": score, "G": f"{g_rate:.0f}%", "Giá": f"{t_df['Close'].iloc[-1]:,.0f}"})
            except: continue
    st.dataframe(pd.DataFrame(radar_data).sort_values(by="Điểm", ascending=False), use_container_width=True, hide_index=True)

with tab_analysis:
    try:
        s_obj = yf.Ticker(f"{t_input}.VN")
        data = s_obj.history(period="1y")
        if isinstance(data.columns, pd.MultiIndex): data.columns = data.columns.get_level_values(0)
        curr_p = float(data['Close'].iloc[-1])
        is_df = s_obj.financials; bs = s_obj.balance_sheet
        
        g_val = ((is_df.loc['Total Revenue'].iloc[0] / is_df.loc['Total Revenue'].iloc[4]) - 1)
        margin = ((is_df.loc['Total Revenue'].iloc[0] - is_df.loc['Cost Of Revenue'].iloc[0]) / is_df.loc['Total Revenue'].iloc[0]) * 100
        debt_ratio = (bs.loc['Total Debt'].iloc[0] / bs.loc['Stockholders Equity'].iloc[0]) if 'Total Debt' in bs.index else 0
        
        trust = 0
        if g_val > 0.25: trust += 30
        if margin > 15: trust += 20
        if debt_ratio < 1.2: trust += 20
        if curr_p > data['Close'].rolling(50).mean().iloc[-1]: trust += 30
        
        st.markdown(f"### 🛡️ Niềm tin Tầm soát: {trust}%")
        st.progress(trust / 100)
        
        st.write(f"📍 Giá hiện tại: **{curr_p:,.0f}**")
        m1, m2 = st.columns(2)
        m1.metric("🐢 Thận trọng", f"{curr_p * (1 + g_val * 0.4) * inf_factor:,.0f}")
        m2.metric("🏠 Cơ sở", f"{curr_p * (1 + g_val) * inf_factor:,.0f}")
        st.metric("🚀 Phi thường", f"{curr_p * (1 + g_val * 2) * inf_factor:,.0f}")

        with st.expander("📝 Phân tích sâu BCTC", expanded=True):
            st.write(f"• Biên lãi gộp: **{margin:.1f}%** | Nợ/Vốn CSH: **{debt_ratio:.2f}x**")
            advice = []
            if margin > 20: advice.append("Lợi thế cạnh tranh cao.")
            if debt_ratio > 1.5: advice.append("🚨 Chú ý nợ.")
            st.write("👉 " + " | ".join(advice))

        # Đồ thị Ichimoku (Nền sáng dễ nhìn hơn)
        data['ATR'] = pd.concat([(data['High']-data['Low']), (data['High']-data['Close'].shift()).abs(), (data['Low']-data['Close'].shift()).abs()], axis=1).max(axis=1).rolling(14).mean()
        h9 = data['High'].rolling(9).max(); l9 = data['Low'].rolling(9).min(); data['tenkan'] = (h9+l9)/2
        h26 = data['High'].rolling(26).max(); l26 = data['Low'].rolling(26).min(); data['kijun'] = (h26+l26)/2
        data['sa'] = ((data['tenkan'] + data['kijun'])/2).shift(26)
        data['sb'] = ((data['High'].rolling(52).max() + data['Low'].rolling(52).min())/2).shift(26)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data.index, y=data['sa'], line=dict(width=0), showlegend=False))
        fig.add_trace(go.Scatter(x=data.index, y=data['sb'], line=dict(width=0), fill='tonexty', fillcolor='rgba(0, 123, 255, 0.1)', name='Mây'))
        fig.add_trace(go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], name='Giá'))
        fig.update_layout(template="plotly_white", height=400, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

        rev_5q = is_df.loc['Total Revenue'].iloc[:5][::-1]
        fig_q = go.Figure(data=[go.Bar(x=rev_5q.index.strftime('%Q/%Y'), y=rev_5q, marker_color='#007bff')])
        fig_q.update_layout(title="Chu kỳ 5 quý", height=250, template="plotly_white")
        st.plotly_chart(fig_q, use_container_width=True)

        if st.button(f"📌 Lưu {t_input}"):
            st.session_state.history_log.append({"Mã": t_input, "Giá": curr_p, "Ngày": datetime.now().strftime("%d/%m")})
    except: st.info("Chọn mã ở Sidebar.")

with tab_history:
    if st.session_state.history_log: st.table(pd.DataFrame(st.session_state.history_log))