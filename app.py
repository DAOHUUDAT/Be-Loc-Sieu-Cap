import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- 1. CẤU HÌNH GIAO DIỆN SÁNG CHUYÊN NGHIỆP ---
st.set_page_config(page_title="HÃY CHỌN CÁ ĐÚNG v5.9.2", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #fcfcfc; color: #1e1e1e; }
    [data-testid="stMetricValue"] { font-size: 1.8rem !important; color: #007bff !important; font-weight: bold; }
    .stTabs [data-baseweb="tab-list"] { background-color: #ffffff; border-radius: 10px; padding: 5px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
    .stTabs [data-baseweb="tab"] { color: #444; font-weight: 600; font-size: 1rem; }
    .stTabs [data-baseweb="tab--active"] { color: #007bff !important; border-bottom: 2px solid #007bff; }
    .stExpander { background-color: #ffffff !important; border: 1px solid #e0e0e0 !important; border-radius: 12px !important; }
    </style>
    """, unsafe_allow_html=True)

if 'history_log' not in st.session_state: st.session_state['history_log'] = []

# --- 2. SIDEBAR: CẨM NANG & ĐIỀU KHIỂN (KHÔI PHỤC HOÀN TOÀN) ---
with st.sidebar:
    st.header("🎮 ĐÀI CHỈ HUY")
    t_input = st.text_input("🔍 SOI MÃ CÁ", "VGC").upper()
    st.divider()
    st.header("📓 CẨM NANG CHIẾN THUẬT")
    with st.expander("📖 Giải mã thông số", expanded=True):
        st.markdown("""
        * **🛡️ Niềm tin > 80%:** Cá Siêu cấp.
        * **🌊 Sóng Ngầm:** Vol > 150%.
        * **🥇 ĐẠI CA:** Dẫn đầu Elite 20.
        * **📈 Co giãn:** Theo nhiệt độ VNI.
        * **✂️ ATR:** Cắt lỗ kỷ luật (2x ATR).
        * **🎯 Target:** Chốt lời (3x ATR).
        """)

st.title("🔱 HÃY CHỌN CÁ ĐÚNG v5.9.2")

# --- 3. TRẠM QUAN TRẮC ĐẠI DƯƠNG (KHÔI PHỤC VSA & CO GIÃN) ---
try:
    vni = yf.download("^VNI", period="150d", progress=False)
    if not vni.empty:
        if isinstance(vni.columns, pd.MultiIndex): vni.columns = vni.columns.get_level_values(0)
        v_c = float(vni['Close'].iloc[-1])
        # Khôi phục đúng công thức mây VNI
        vh26_v = vni['High'].rolling(26).max(); vl26_v = vni['Low'].rolling(26).min()
        vh9_v = vni['High'].rolling(9).max(); vl9_v = vni['Low'].rolling(9).min()
        vsa = (((vh9_v+vl9_v)/2 + (vh26_v+vl26_v)/2)/2).shift(26).iloc[-1]
        
        inf_factor = 1.1 if v_c > vsa else 0.85
        st.info(f"🌊 **Đại Dương:** {'🟢 THẢ LƯỚI (Vùng an toàn)' if v_c > vsa else '🔴 ĐÁNH KẺNG (Rủi ro)'}")
        c1, c2 = st.columns(2)
        c1.metric("VN-Index", f"{v_c:.1f}")
        c2.metric("Hệ số Co giãn", f"{inf_factor}x")
except: pass

# --- 4. HỆ THỐNG TABS ---
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
        
        # Công thức Niềm tin & BCTC (Bọc thép)
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
        
        # Ma trận Định giá
        st.write(f"📍 Giá hiện tại: **{curr_p:,.0f}**")
        m1, m2 = st.columns(2)
        m1.metric("🐢 Thận trọng", f"{curr_p * (1 + g_val * 0.4) * inf_factor:,.0f}")
        m2.metric("🏠 Cơ sở", f"{curr_p * (1 + g_val) * inf_factor:,.0f}")
        st.metric("🚀 Phi thường", f"{curr_p * (1 + g_val * 2) * inf_factor:,.0f}")

        with st.expander("📝 Phân tích sâu BCTC", expanded=True):
            st.write(f"• Biên lãi gộp: **{margin:.1f}%** | Nợ/Vốn CSH: **{debt_ratio:.2f}x**")
            advice = []
            if margin > 20: advice.append("Lợi thế cạnh tranh mạnh.")
            if debt_ratio > 1.5: advice.append("🚨 Cảnh báo nợ vay.")
            if g_val > 0.3: advice.append("Thức ăn cực dồi dào.")
            st.write("👉 **Kết luận:** " + " | ".join(advice))

        # --- KHÔI PHỤC FULL BIỂU ĐỒ ICHIMOKU & ATR ---
        data['ATR'] = pd.concat([(data['High']-data['Low']), (data['High']-data['Close'].shift()).abs(), (data['Low']-data['Close'].shift()).abs()], axis=1).max(axis=1).rolling(14).mean()
        h9 = data['High'].rolling(9).max(); l9 = data['Low'].rolling(9).min(); data['tenkan'] = (h9+l9)/2
        h26 = data['High'].rolling(26).max(); l26 = data['Low'].rolling(26).min(); data['kijun'] = (h26+l26)/2
        data['sa'] = ((data['tenkan'] + data['kijun'])/2).shift(26)
        data['sb'] = ((data['High'].rolling(52).max() + data['Low'].rolling(52).min())/2).shift(26)
        
        fig = go.Figure()
        # Mây Kumo
        fig.add_trace(go.Scatter(x=data.index, y=data['sa'], line=dict(width=0), showlegend=False))
        fig.add_trace(go.Scatter(x=data.index, y=data['sb'], line=dict(width=0), fill='tonexty', fillcolor='rgba(0, 123, 255, 0.1)', name='Mây'))
        # Nến & Đường Ichimoku
        fig.add_trace(go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], name='Giá'))
        fig.add_trace(go.Scatter(x=data.index, y=data['tenkan'], line=dict(color='pink', width=1), name='Tenkan'))
        fig.add_trace(go.Scatter(x=data.index, y=data['kijun'], line=dict(color='yellow', width=1), name='Kijun'))
        
        # Target & Cutloss
        catr = float(data['ATR'].iloc[-1])
        fig.add_hline(y=curr_p + (3*catr), line_dash="dash", line_color="cyan", annotation_text="TARGET (3x ATR)")
        fig.add_hline(y=curr_p - (2*catr), line_dash="dash", line_color="red", annotation_text="CUT LOSS (2x ATR)")
        
        fig.update_layout(template="plotly_white", height=450, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

        # Biểu đồ Doanh thu 5 quý
        rev_5q = is_df.loc['Total Revenue'].iloc[:5][::-1]
        fig_q = go.Figure(data=[go.Bar(x=rev_5q.index.strftime('%Q/%Y'), y=rev_5q, marker_color='#007bff')])
        fig_q.update_layout(title="Chu kỳ doanh thu 5 quý", height=250, template="plotly_white")
        st.plotly_chart(fig_q, use_container_width=True)

        if st.button(f"📌 Lưu {t_input} vào Sổ Vàng"):
            st.session_state.history_log.append({"Mã": t_input, "Giá": curr_p, "Ngày": datetime.now().strftime("%d/%m")})
    except Exception as e: st.error(f"Chọn mã ở Sidebar để soi chi tiết đệ tử... ({e})")

with tab_history:
    if st.session_state.history_log:
        st.subheader("📓 Nhật ký Tầm soát")
        st.table(pd.DataFrame(st.session_state.history_log))