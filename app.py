import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- 1. CẤU HÌNH ADAPTIVE (Sáng/Tối đều cân được) ---
st.set_page_config(page_title="HÃY CHỌN CÁ ĐÚNG v6.1", layout="wide")

# CSS thông minh: Tự nhận diện nền để đổi màu chữ
st.markdown("""
    <style>
    .stApp { transition: all 0.5s; }
    [data-testid="stMetricValue"] { font-size: 1.8rem !important; font-weight: bold; }
    /* Fix lỗi chữ khó nhìn trong Expander */
    .stExpander { border-radius: 10px !important; border: 1px solid #444; }
    .stDataFrame { border-radius: 10px; }
    /* Đảm bảo ảnh luôn nằm giữa */
    .stImage > img { border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); }
    </style>
    """, unsafe_allow_html=True)

if 'history_log' not in st.session_state: st.session_state['history_log'] = []

# --- 2. HÀM LẤY DỮ LIỆU AN TOÀN (CHỐNG LỖI NAN) ---
def get_safe_data(ticker):
    try:
        obj = yf.Ticker(f"{ticker}.VN")
        df = obj.history(period="1y")
        if df.empty or len(df) < 50: return None, None, None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        return obj, df, obj.info
    except: return None, None, None

# --- 3. SIDEBAR: CẨM NANG VÀ ĐIỀU KHIỂN ---
with st.sidebar:
    st.header("🎮 ĐÀI CHỈ HUY")
    t_input = st.text_input("🔍 SOI MÃ CÁ", "VGC").upper()
    st.divider()
    st.header("📓 CẨM NANG CHIẾN THUẬT")
    with st.expander("📖 Giải mã thông số", expanded=True):
        st.markdown("""
        * **🛡️ Niềm tin > 80%:** Cá Lớn thực thụ.
        * **🌊 Sóng Ngầm:** Vol bùng nổ > 150%.
        * **📈 Co giãn:** Tự động theo Index.
        * **✂️ ATR:** Điểm tựa quản trị rủi ro.
        """)

st.title("🔱 HÃY CHỌN CÁ ĐÚNG v6.1")

# --- 4. TRẠM QUAN TRẮC VN-INDEX (Hàn ống Co giãn) ---
inf_factor = 1.0
try:
    vni_df = yf.download("^VNI", period="100d", progress=False)
    if not vni_df.empty:
        if isinstance(vni_df.columns, pd.MultiIndex): vni_df.columns = vni_df.columns.get_level_values(0)
        v_close = vni_df['Close'].iloc[-1]
        v_h26 = vni_df['High'].rolling(26).max(); v_l26 = vni_df['Low'].rolling(26).min()
        v_h9 = vni_df['High'].rolling(9).max(); v_l9 = vni_df['Low'].rolling(9).min()
        v_sa = (((v_h9+v_l9)/2 + (v_h26+v_l26)/2)/2).shift(26).iloc[-1]
        inf_factor = 1.15 if v_close > v_sa else 0.85
        st.write(f"🌊 **Trạng thái biển:** {'🟢 THẢ LƯỚI' if v_close > v_sa else '🔴 ĐÁNH KẺNG'}")
except: st.warning("⚠️ Mất kết nối radar đại dương!")

# --- 5. HỆ THỐNG TABS ---
tab_radar, tab_analysis, tab_history = st.tabs(["🎯 RADAR ELITE", "💎 SOI CHI TIẾT", "📓 SỔ VÀNG"])

with tab_radar:
    # SỬA LỖI ẢNH: Sử dụng link trực tiếp hoặc link GitHub
    st.image("https://github.com/DAOHUUDAT/Be-Loc-Sieu-Cap/blob/main/anh-tri-ky.jpg?raw=true", 
             caption="Sự kết hợp giữa Trí tuệ con người & AI", use_container_width=True)
    
    st.subheader("🤖 Top 20 Đệ Tử Cá (Dòng chảy v5.5.1)")
    elite_20 = ["DGC", "MWG", "FPT", "TCB", "SSI", "HPG", "GVR", "CTR", "DBC", "VNM", "STB", "MBB", "ACB", "KBC", "VGC", "PVS", "PVD", "ANV", "VHC", "REE"]
    radar_list = []
    with st.spinner('Đang quét lưới...'):
        for tk in elite_20:
            _, df_tk, _ = get_safe_data(tk)
            if df_tk is not None:
                v_now = df_tk['Volume'].iloc[-1]; v_avg = df_tk['Volume'].rolling(20).mean().iloc[-1]
                score = 3 if v_now > v_avg * 1.5 else 1
                radar_list.append({"Mã": tk, "Điểm": score, "Giá": f"{df_tk['Close'].iloc[-1]:,.0f}", "Sóng": "🌊" if v_now > v_avg * 1.5 else "☕"})
    st.dataframe(pd.DataFrame(radar_list).sort_values("Điểm", ascending=False), use_container_width=True, hide_index=True)

with tab_analysis:
    s_obj, s_df, s_info = get_safe_data(t_input)
    if s_df is not None:
        curr_p = s_df['Close'].iloc[-1]
        
        # --- KHÔI PHỤC ĐƯỜNG ỐNG NIỀM TIN v5.5.1 ---
        try:
            fin = s_obj.quarterly_financials
            rev_g = (fin.loc['Total Revenue'].iloc[0] / fin.loc['Total Revenue'].iloc[4] - 1) if len(fin.columns) > 4 else 0.1
            trust_score = int(min(100, (rev_g * 100) + (50 if curr_p > s_df['Close'].rolling(50).mean().iloc[-1] else 0)))
        except: trust_score = 50; rev_g = 0.1

        st.subheader(f"🛡️ Niềm tin {t_input}: {trust_score}%")
        st.progress(trust_score / 100)

        # ĐỊNH GIÁ CO GIÃN (HÀN LẠI)
        st.write(f"📍 Giá hiện tại: **{curr_p:,.0f}**")
        c1, c2, c3 = st.columns(3)
        c1.metric("🐢 Thận trọng", f"{curr_p * (1 + rev_g * 0.5) * inf_factor:,.0f}")
        c2.metric("🏠 Cơ sở", f"{curr_p * (1 + rev_g) * inf_factor:,.0f}")
        c3.metric("🚀 Phi thường", f"{curr_p * (1 + rev_g * 2) * inf_factor:,.0f}")

        # --- BIỂU ĐỒ ICHIMOKU & ATR (FULL ỐNG) ---
        s_df['ATR'] = pd.concat([(s_df['High']-s_df['Low']), (s_df['High']-s_df['Close'].shift()).abs(), (s_df['Low']-s_df['Close'].shift()).abs()], axis=1).max(axis=1).rolling(14).mean()
        h9 = s_df['High'].rolling(9).max(); l9 = s_df['Low'].rolling(9).min(); s_df['tenkan'] = (h9+l9)/2
        h26 = s_df['High'].rolling(26).max(); l26 = s_df['Low'].rolling(26).min(); s_df['kijun'] = (h26+l26)/2
        s_df['sa'] = ((s_df['tenkan'] + s_df['kijun'])/2).shift(26)
        s_df['sb'] = ((s_df['High'].rolling(52).max() + s_df['Low'].rolling(52).min())/2).shift(26)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=s_df.index, y=s_df['sa'], line=dict(width=0), showlegend=False))
        fig.add_trace(go.Scatter(x=s_df.index, y=s_df['sb'], line=dict(width=0), fill='tonexty', fillcolor='rgba(0, 150, 255, 0.15)', name='Mây Kumo'))
        fig.add_trace(go.Candlestick(x=s_df.index, open=s_df['Open'], high=s_df['High'], low=s_df['Low'], close=s_df['Close'], name='Giá'))
        fig.add_trace(go.Scatter(x=s_df.index, y=s_df['tenkan'], line=dict(color='#ff33cc', width=1.5), name='Tenkan'))
        fig.add_trace(go.Scatter(x=s_df.index, y=s_df['kijun'], line=dict(color='#ffcc00', width=1.5), name='Kijun'))
        
        # Target/Cutloss
        atr_v = float(s_df['ATR'].iloc[-1])
        fig.add_hline(y=curr_p + (3*atr_v), line_dash="dash", line_color="#00ffff", annotation_text="TARGET")
        fig.add_hline(y=curr_p - (2*atr_v), line_dash="dash", line_color="#ff4444", annotation_text="CUT LOSS")
        
        fig.update_layout(template="plotly_dark" if st.get_option("theme.base") == "dark" else "plotly_white", 
                          height=500, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error(f"❌ Không tìm thấy dữ liệu cho mã {t_input}. Hãy kiểm tra lại kết nối mạng!")

with tab_history:
    st.table(pd.DataFrame(st.session_state.history_log) if st.session_state.history_log else "Sổ vàng đang trống.")