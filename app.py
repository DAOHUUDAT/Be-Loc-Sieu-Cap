import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- 1. KHỞI TẠO LINH HỒN BỂ LỌC ---
st.set_page_config(page_title="Bể Lọc Anh Đạt v5.7.1 - Ultimate Emperor", layout="wide")
if 'history_log' not in st.session_state: st.session_state['history_log'] = []
inf_factor = 1.0 # Hệ số mặc định bảo vệ ống dẫn

# --- 2. CẨM NANG CHIẾN THUẬT (Sidebar) ---
st.sidebar.header("📓 CẨM NANG HOÀNG ĐẾ")
with st.sidebar.expander("🔍 Giải mã Thang đo & Chỉ số", expanded=True):
    st.markdown("""
    - **🛡️ Niềm tin > 80%:** Siêu cá, hội tụ đủ Thiên thời - Địa lợi - Nhân hòa.
    - **🌊 Sóng Ngầm:** Cá mập gom hàng (Vol > 150%).
    - **🥦 Thức ăn sạch:** Tăng trưởng G > 25%.
    - **📈 Co giãn lạm phát:** Tự động chiết khấu giá theo VN-Index.
    - **🥇 ĐẠI CA:** Đệ tử ưu tú nhất trong Elite 20.
    """)

st.title("🔱 HÃY CHỌN CÁ ĐÚNG v5.7.1: HOÀNG ĐẾ TỐI THƯỢNG")

# --- 3. TRẠM QUAN TRẮC ĐẠI DƯƠNG (Bọc thép) ---
try:
    vni = yf.download("^VNI", period="150d", progress=False)
    if not vni.empty:
        if isinstance(vni.columns, pd.MultiIndex): vni.columns = vni.columns.get_level_values(0)
        v_c = float(vni['Close'].iloc[-1])
        vh26_v = vni['High'].rolling(26).max(); vl26_v = vni['Low'].rolling(26).min()
        vh9_v = vni['High'].rolling(9).max(); vl9_v = vni['Low'].rolling(9).min()
        vsa = (((vh9_v+vl9_v)/2 + (vh26_v+vl26_v)/2)/2).shift(26).iloc[-1]
        
        inf_factor = 1.1 if v_c > vsa else 0.85
        st.subheader(f"🌊 Đại Dương: {'🟢 THẢ LƯỚI' if v_c > vsa else '🔴 ĐÁNH KẺNG'}")
        c1, c2, c3 = st.columns(3)
        c1.metric("VN-Index", f"{v_c:.2f}")
        c2.info(f"Hệ số Co giãn: {inf_factor}x")
        c3.success("TRONG ẤM NGOÀI ÊM" if v_c > vsa else "CẢNH BÁO RỦI RO")
except: st.warning("📡 Vệ tinh đại dương đang kết nối lại... Hệ số mặc định: 1.0x")

# --- 4. RADAR PHÂN BẬC ELITE 20 (Ưu tiên Đại ca) ---
st.subheader("🤖 Radar Tầm Soát 20 Đệ Tử Cá")
elite_20 = ["DGC", "MWG", "FPT", "TCB", "SSI", "HPG", "GVR", "CTR", "DBC", "VNM", "STB", "MBB", "ACB", "KBC", "VGC", "PVS", "PVD", "ANV", "VHC", "REE"]
radar_data = []

with st.spinner('Đang quét 20 đệ tử...'):
    for ticker in elite_20:
        try:
            t_obj = yf.Ticker(f"{ticker}.VN")
            t_df = t_obj.history(period="60d")
            if isinstance(t_df.columns, pd.MultiIndex): t_df.columns = t_df.columns.get_level_values(0)
            v_now = t_df['Volume'].iloc[-1]; v_avg = t_df['Volume'].rolling(20).mean().iloc[-1]
            fin = t_obj.quarterly_financials
            g_rate = ((fin.loc['Total Revenue'].iloc[0] / fin.loc['Total Revenue'].iloc[4]) - 1) * 100
            score = (2 if v_now > v_avg * 1.5 else 0) + (3 if g_rate > 30 else 1)
            radar_data.append({
                "Ưu tiên": "🥇 ĐẠI CA" if score >= 4 else "🥈 CẬN VỆ",
                "Mã": ticker, "Điểm": score, "Sóng": "🌊 MẠNH" if v_now > v_avg * 1.5 else "Yên ắng",
                "Thức ăn (G)": f"{g_rate:.1f}%", "Giá": f"{t_df['Close'].iloc[-1]:,.0f}"
            })
        except: continue

df_radar = pd.DataFrame(radar_data).sort_values(by="Điểm", ascending=False)
st.dataframe(df_radar, use_container_width=True)

# --- 5. CHI TIẾT ĐỊNH GIÁ, BCTC & NIỀM TIN (Phun óp xừn) ---
st.divider()
t_input = st.sidebar.text_input("Soi chi tiết Cá", "VGC").upper()
try:
    s_obj = yf.Ticker(f"{t_input}.VN")
    data = s_obj.history(period="1y")
    if isinstance(data.columns, pd.MultiIndex): data.columns = data.columns.get_level_values(0)
    curr_p = float(data['Close'].iloc[-1])
    is_df = s_obj.financials; bs = s_obj.balance_sheet
    
    # Tính toán chỉ số vàng BCTC
    g_val = ((is_df.loc['Total Revenue'].iloc[0] / is_df.loc['Total Revenue'].iloc[4]) - 1)
    margin = ((is_df.loc['Total Revenue'].iloc[0] - is_df.loc['Cost Of Revenue'].iloc[0]) / is_df.loc['Total Revenue'].iloc[0]) * 100
    debt = bs.loc['Total Debt'].iloc[0] if 'Total Debt' in bs.index else 0
    equity = bs.loc['Stockholders Equity'].iloc[0]
    debt_ratio = debt / equity
    
    # THUẬT TOÁN THANG ĐO NIỀM TIN v5.7
    trust = 0
    if g_val > 0.25: trust += 30
    if margin > 15: trust += 20
    if debt_ratio < 1.2: trust += 20
    if curr_p > data['Close'].rolling(50).mean().iloc[-1]: trust += 30
    
    st.subheader(f"🛡️ Thang Đo Niềm Tin Tầm Soát: {trust}%")
    st.progress(trust / 100)
    if trust >= 80: st.success("💎 SIÊU CÁ: Hội tụ đủ các yếu tố Trọng yếu để bứt phá.")
    elif trust >= 50: st.warning("🐢 TIỀM NĂNG: Cá khỏe, cần quan sát thêm dòng tiền.")
    else: st.error("🚨 CẨN TRỌNG: Chỉ số tài chính hoặc vị thế đang yếu.")

    # Ma trận định giá
    st.info(f"📍 Giá hiện tại của cá: **{curr_p:,.0f}**")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("📍 Giá Hiện Tại", f"{curr_p:,.0f}")
    m2.metric("🐢 Thận trọng", f"{curr_p * (1 + g_val * 0.4) * inf_factor:,.0f}")
    m3.metric("🏠 Cơ sở", f"{curr_p * (1 + g_val) * inf_factor:,.0f}")
    m4.metric("🚀 Phi thường", f"{curr_p * (1 + g_val * 2) * inf_factor:,.0f}")

    # Lời phê Hội đồng quản trị
    with st.expander("📝 Phân Tích Báo Cáo Tài Chính Chi Tiết", expanded=True):
        f1, f2, f3 = st.columns(3)
        f1.metric("Biên Lãi Gộp", f"{margin:.1f}%")
        f2.metric("Nợ/Vốn CSH", f"{debt_ratio:.2f}x")
        f3.metric("Tăng trưởng G", f"{g_val*100:.1f}%")
        advice = []
        if margin > 20: advice.append("Lợi thế cạnh tranh mạnh.")
        if debt_ratio > 1.5: advice.append("🚨 Rủi ro nợ vay cao.")
        if g_val > 0.3: advice.append("Thức ăn (doanh thu) dồi dào.")
        st.write("👉 **Kết luận:** " + " | ".join(advice))

    # Biểu đồ cột 5 quý
    rev_5q = is_df.loc['Total Revenue'].iloc[:5][::-1]
    fig_q = go.Figure(data=[go.Bar(x=rev_5q.index.strftime('%Q/%Y'), y=rev_5q, marker_color='gold')])
    fig_q.update_layout(title="Chu kỳ doanh thu 5 quý", height=250, template="plotly_dark")
    st.plotly_chart(fig_q, use_container_width=True)

    # Đồ thị Ichimoku & ATR (Vá lỗi Syntax tại đây)
    data['ATR'] = pd.concat([(data['High']-data['Low']), (data['High']-data['Close'].shift()).abs(), (data['Low']-data['Close'].shift()).abs()], axis=1).max(axis=1).rolling(14).mean()
    h9 = data['High'].rolling(9).max(); l9 = data['Low'].rolling(9).min(); data['tenkan'] = (h9+l9)/2
    h26 = data['High'].rolling(26).max(); l26 = data['Low'].rolling(26).min(); data['kijun'] = (h26+l26)/2
    data['sa'] = ((data['tenkan'] + data['kijun'])/2).shift(26)
    data['sb'] = ((data['High'].rolling(52).max() + data['Low'].rolling(52).min())/2).shift(26)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=data['sa'], line=dict(width=0), showlegend=False))
    fig.add_trace(go.Scatter(x=data.index, y=data['sb'], line=dict(width=0), fill='tonexty', fillcolor='rgba(0, 255, 0, 0.1)', name='Mây'))
    fig.add_trace(go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], name='Giá'))
    catr = float(data['ATR'].iloc[-1])
    fig.add_hline(y=curr_p + (3*catr), line_dash="dash", line_color="cyan", annotation_text="TARGET")
    fig.add_hline(y=curr_p - (2*catr), line_dash="dash", line_color="red", annotation_text="CUT LOSS")
    fig.update_layout(template="plotly_dark", height=500, xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

    if st.button(f"📌 Lưu {t_input} vào Sổ Vàng"):
        st.session_state.history_log.append({"Mã": t_input, "Giá": curr_p, "Ngày": datetime.now().strftime("%d/%m")})
except Exception as e: st.error(f"Đang đồng bộ dữ liệu BCTC cho đệ tử... {e}")

# --- 6. SỔ VÀNG KIM CƯƠNG ---
if st.session_state.history_log:
    st.divider(); st.subheader("📓 Sổ Vàng Cá Lớn"); st.table(pd.DataFrame(st.session_state.history_log))