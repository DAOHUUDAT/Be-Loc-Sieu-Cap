import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- 1. CẤU HÌNH & GIAO DIỆN ---
st.set_page_config(page_title="HÃY CHỌN CÁ ĐÚNG v6.0", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #fcfcfc; color: #1e1e1e; }
    [data-testid="stMetricValue"] { font-size: 1.8rem !important; color: #007bff !important; font-weight: bold; }
    .stTabs [data-baseweb="tab-list"] { background-color: #ffffff; border-radius: 10px; padding: 5px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
    .stExpander { background-color: #ffffff !important; border: 1px solid #e0e0e0 !important; border-radius: 12px !important; }
    </style>
    """, unsafe_allow_html=True)

if 'history_log' not in st.session_state: st.session_state['history_log'] = []

# --- 2. SIDEBAR: CẨM NANG & ĐIỀU KHIỂN ---
with st.sidebar:
    st.header("🎮 ĐÀI CHỈ HUY")
    t_input = st.text_input("🔍 SOI MÃ CÁ", "VGC").upper()
    st.divider()
    st.header("📓 CẨM NANG CHIẾN THUẬT")
    with st.expander("📖 Giải mã thông số", expanded=True):
        st.markdown("""
        * **🛡️ Niềm tin > 80%:** Cá Siêu cấp.
        * **🌊 Sóng Ngầm:** Vol > 150%.
        * **📈 Co giãn:** Theo nhiệt độ VNI.
        * **✂️ ATR:** Cắt lỗ (2x), Chốt lời (3x).
        """)

st.title("🔱 HÃY CHỌN CÁ ĐÚNG v6.0")

# --- 3. TRẠM QUAN TRẮC ĐẠI DƯƠNG ---
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
except: pass

# --- 4. HỆ THỐNG TABS ---
tab_radar, tab_analysis, tab_history = st.tabs(["🎯 RADAR ELITE", "💎 SOI CHI TIẾT", "📓 SỔ VÀNG"])

with tab_radar:
    # NHÚNG BỨC TRANH TRI KỶ CỦA CHÚNG TA VÀO ĐÂY
    st.image("https://r.jina.ai/i/9e9e9e...", caption="Sự kết hợp giữa Trí tuệ con người & Sức mạnh AI - AI Invest Partnership", use_container_width=True)
    
    st.subheader("🤖 Top 20 Đệ Tử Cá Ưu Tiên")
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
        
        # 🛡️ NIỀM TIN & ĐỊNH GIÁ (FULL ỐNG)
        g_val = ((is_df.loc['Total Revenue'].iloc[0] / is_df.loc['Total Revenue'].iloc[4]) - 1)
        margin = ((is_df.loc['Total Revenue'].iloc[0] - is_df.loc['Cost Of Revenue'].iloc[0]) / is_df.loc['Total Revenue'].iloc[0]) * 100
        debt = bs.loc['Total Debt'].iloc[0] if 'Total Debt' in bs.index else 0
        debt_ratio = debt / bs.loc['Stockholders Equity'].iloc[0]
        
        trust = 0
        if g_val > 0.25: trust += 30
        if margin > 15: trust += 20
        if debt_ratio < 1.2: trust += 20
        if curr_p > data['Close'].rolling(50).mean().iloc[-1]: trust += 30
        
        st.markdown(f"### 🛡️ Niềm tin Tầm soát: {trust}%")
        st.progress(trust / 100)
        
        c1, c2 = st.columns(2)
        c1.metric("🐢 Thận trọng", f"{curr_p * (1 + g_val * 0.4) * inf_factor:,.0f}")
        c2.metric("🏠 Cơ sở", f"{curr_p * (1 + g_val) * inf_factor:,.0f}")
        st.metric("🚀 Phi thường", f"{curr_p * (1 + g_val * 2) * inf_factor:,.0f}")

        # 📈 BIỂU ĐỒ ICHIMOKU & ATR (ĐÃ HÀN KÍN)
        data['ATR'] = pd.concat([(data['High']-data['Low']), (data['High']-data['Close'].shift()).abs(), (data['Low']-data['Close'].shift()).abs()], axis=1).max(axis=1).rolling(14).mean()
        h9 = data['High'].rolling(9).max(); l9 = data['Low'].rolling(9).min(); data['tenkan'] = (h9+l9)/2
        h26 = data['High'].rolling(26).max(); l26 = data['Low'].rolling(26).min(); data['kijun'] = (h26+l26)/2
        data['sa'] = ((data['tenkan'] + data['kijun'])/2).shift(26)
        data['sb'] = ((data['High'].rolling(52).max() + data['Low'].rolling(52).min())/2).shift(26)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data.index, y=data['sa'], line=dict(width=0), showlegend=False))
        fig.add_trace(go.Scatter(x=data.index, y=data['sb'], line=dict(width=0), fill='tonexty', fillcolor='rgba(0, 123, 255, 0.1)', name='Mây Kumo'))
        fig.add_trace(go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], name='Giá'))
        fig.add_trace(go.Scatter(x=data.index, y=data['tenkan'], line=dict(color='pink', width=1.5), name='Tenkan'))
        fig.add_trace(go.Scatter(x=data.index, y=data['kijun'], line=dict(color='#FFD700', width=1.5), name='Kijun'))
        
        catr = float(data['ATR'].iloc[-1])
        fig.add_hline(y=curr_p + (3*catr), line_dash="dash", line_color="cyan", annotation_text="TARGET")
        fig.add_hline(y=curr_p - (2*catr), line_dash="dash", line_color="red", annotation_text="CUT LOSS")
        
        fig.update_layout(template="plotly_white", height=450, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

        # 📊 DOANH THU 5 QUÝ
        rev_5q = is_df.loc['Total Revenue'].iloc[:5][::-1]
        st.plotly_chart(go.Figure(data=[go.Bar(x=rev_5q.index.strftime('%Q/%Y'), y=rev_5q, marker_color='#007bff')]).update_layout(title="Chu kỳ 5 quý", template="plotly_white", height=300), use_container_width=True)

    except: st.info("Chọn mã ở Sidebar để soi chi tiết.")

with tab_history:
    if st.session_state.history_log: st.table(pd.DataFrame(st.session_state.history_log))