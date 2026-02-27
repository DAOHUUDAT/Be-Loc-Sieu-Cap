import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import google.generativeai as genai

# --- CẤU HÌNH GOOGLE GEMINI ---
# Bro hãy đảm bảo đã set API Key trong secrets của Streamlit hoặc môi trường
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.warning("⚠️ Chưa tìm thấy API Key của Gemini. Tính năng mổ xẻ sẽ bị hạn chế.")

@st.cache_data # Dùng cache để app chỉ tải một lần, cực nhanh
def load_vietstock_data():
    urls = [
        "https://github.com/DAOHUUDAT/Be-Loc-Sieu-Cap/raw/refs/heads/main/data/HOSE.xlsx",
        "https://github.com/DAOHUUDAT/Be-Loc-Sieu-Cap/raw/refs/heads/main/data/HNX.xlsx",
        "https://github.com/DAOHUUDAT/Be-Loc-Sieu-Cap/raw/refs/heads/main/data/UPCOM.xlsx"
    ]
    try:
        # Gộp 3 sàn thành 1 đại dương dữ liệu duy nhất
        combined_df = pd.concat([pd.read_excel(url) for url in urls], ignore_index=True)
        # Làm sạch tên cột
        combined_df.columns = [str(c).strip() for c in combined_df.columns]
        return combined_df
    except Exception as e:
        st.error(f"Lỗi tải dữ liệu: {e}")
        return pd.DataFrame()

# Kích hoạt dữ liệu nền
vietstock_db = load_vietstock_data()

# --- CÁC HÀM BỔ TRỢ ---
def get_star_rating(g_margin, debt_ratio, ttm_profit):
    stars = 0
    try:
        if float(g_margin) > 15: stars += 2
        elif float(g_margin) > 10: stars += 1
        
        if float(debt_ratio) < 1.0: stars += 2
        elif float(debt_ratio) < 1.5: stars += 1
        
        if float(ttm_profit) > 0: stars += 1
    except:
        return "⭐"
    return "⭐" * max(stars, 1)

def expert_moxe_analysis(ticker, row_data):
    """Hàm não bộ để Gemini mổ xẻ cá lớn"""
    try:
        pe = row_data.get('P/E', 'N/A')
        roe = row_data.get('ROE', 'N/A')
        inventory = row_data.get('Hàng tồn kho', 0) / 1e9
        profit = row_data.get('Lợi nhuận sau thuế TT', 0) / 1e9
        
        prompt = f"""
        Bạn là chuyên gia săn cá lớn (siêu cổ phiếu). Hãy mổ xẻ mã {ticker} với dữ liệu:
        - P/E: {pe}, ROE: {roe}%
        - Hàng tồn kho (Của để dành): {inventory:.2f} tỷ
        - Lợi nhuận gần nhất: {profit:.2f} tỷ
        
        Hãy viết bản phân tích theo đúng cấu trúc 7 phần:
        I. KỸ THUẬT (Pha tích lũy hay bứt phá?)
        II. TÀI CHÍNH (Nội công khỏe hay yếu?)
        III. ĐỊNH GIÁ (Rẻ hay đắt?)
        IV. LUẬN ĐIỂM (Tại sao nên mua?)
        V. MỤC TIÊU GIÁ (12 tháng tới)
        VI. ĐÁNH GIÁ TỔNG QUAN
        VII. KẾT LUẬN (Có nên 'thả lưới' không?)
        Dùng ngôn ngữ dân săn cá, thực chiến, quyết đoán!
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ Cá quẫy mạnh quá, Gemini chưa soi được nội tạng: {e}"

# --- GIAO DIỆN STREAMLIT ---
st.set_page_config(page_title="Bể Lọc Siêu Cấp 2026", layout="wide")

# Khởi tạo session state để lưu lịch sử
if 'history_log' not in st.session_state:
    st.session_state.history_log = []
if 'selected_ticker' not in st.session_state:
    st.session_state.selected_ticker = "HSG"

st.title("🌊 BỂ LỌC SIÊU CẤP - SĂN CÁ LỚN 2026")
st.markdown("---")

# Sidebar cấu hình lọc
st.sidebar.header("⚙️ BỘ LỌC ĐẠI DƯƠNG")
min_roe = st.sidebar.slider("ROE tối thiểu (%)", 0, 50, 10)
max_debt = st.sidebar.slider("Nợ/VCSH tối đa", 0.0, 5.0, 1.5)

# Phân định các cột dữ liệu (Tùy chỉnh theo file Excel của Vietstock)
col_ticker = 'Mã' if 'Mã' in vietstock_db.columns else vietstock_db.columns[0]
col_pe = 'P/E'
col_roe = 'ROE'
col_debt = 'Nợ/VCSH'
col_gmargin = 'Biên lợi nhuận gộp'
col_profit = 'Lợi nhuận sau thuế TT'
col_inventory = 'Hàng tồn kho'

# Các Tab chính của App
tab_radar, tab_analysis, tab_history = st.tabs(["🚀 RADAR TÌM CÁ", "🔬 MỔ XẺ NỘI TẠNG", "📓 SỔ VÀNG"])

with tab_radar:
    st.subheader("📡 Radar quét Siêu Cá (Theo chuẩn Trường Money & CANSLIM)")
    
    # Logic lọc cá
    try:
        mask = (vietstock_db[col_roe] >= min_roe) & (vietstock_db[col_debt] <= max_debt)
        display_df = vietstock_db[mask].copy()
        
        # Thêm cột Đánh giá sao (Xử lý lỗi thụt lề tại đây)
        star_list = []
        for index, row in display_df.iterrows():
            try:
                s = get_star_rating(row.get(col_gmargin, 0), row.get(col_debt, 0), row.get(col_profit, 0))
                star_list.append(s)
            except:
                star_list.append("⭐")
        
        display_df['Đánh giá'] = star_list
        
        st.dataframe(display_df[[col_ticker, col_pe, col_roe, col_debt, 'Đánh giá']].sort_values(col_roe, ascending=False), use_container_width=True)
    except Exception as e:
        st.error(f"Lỗi hiển thị Radar: {e}")

with tab_analysis:
    st.subheader("🔬 PHÒNG THÍ NGHIỆM: MỔ XẺ NỘI TẠNG CÁ")
    
    t_input = st.text_input("Nhập mã cá muốn mổ xẻ:", value=st.session_state.selected_ticker).upper()
    
    if t_input:
        st.session_state.selected_ticker = t_input
        row_list = vietstock_db[vietstock_db[col_ticker] == t_input]
        
        if not row_list.empty:
            row = row_list.iloc[0]
            
            c1, c2 = st.columns([1, 2])
            with c1:
                st.write("### 📊 Thông số thực tế")
                st.metric("P/E", f"{row.get(col_pe, 0):.2f}")
                st.metric("ROE (%)", f"{row.get(col_roe, 0):.2f}%")
                st.metric("Của để dành (Tỷ)", f"{row.get(col_inventory, 0)/1e9:,.1f}")
                
                st.divider()
                st.write("### 🧮 Định giá DCF (Dự phóng)")
                fcf_in = st.number_input("FCF dự phóng (Tỷ)", value=1200)
                wacc_in = st.slider("WACC (%)", 8, 15, 12)
                # Giả định 620tr cổ phiếu cho HSG hoặc lấy từ data nếu có
                target_p = (fcf_in * 1000 / wacc_in) / 620
                st.success(f"Giá mục tiêu: **{target_p:,.0f} VNĐ**")
                
                if st.button("📝 Lưu vào Sổ Vàng"):
                    log = {"Ngày": datetime.now().strftime("%d/%m/%Y"), "Mã": t_input, "Giá mục tiêu": f"{target_p:,.0f}"}
                    st.session_state.history_log.append(log)
                    st.toast(f"Đã lưu mã {t_input}!")

            with c2:
                st.write("### 🤖 Ý KIẾN CHUYÊN GIA GEMINI")
                if st.button(f"🚀 Bắt đầu mổ xẻ {t_input}"):
                    with st.spinner("Đang soi nội tạng..."):
                        # Gọi não bộ Gemini
                        ket_qua = expert_moxe_analysis(t_input, row)
                        st.markdown(ket_qua)
                        
                # Vẽ chart kỹ thuật đơn giản
                st.write("---")
                st.write("📈 Biểu đồ giá (YFinance)")
                try:
                    df_chart = yf.download(f"{t_input}.VN", period="6mo")
                    if not df_chart.empty:
                        fig = go.Figure(data=[go.Candlestick(x=df_chart.index, open=df_chart['Open'], high=df_chart['High'], low=df_chart['Low'], close=df_chart['Close'])])
                        fig.update_layout(height=400, margin=dict(l=0, r=0, t=0, b=0))
                        st.plotly_chart(fig, use_container_width=True)
                except:
                    st.info("Không tải được biểu đồ từ Yahoo Finance.")
        else:
            st.warning("Mã này không tồn tại trong dữ liệu 3 sàn.")

with tab_history:
    st.subheader("📓 SỔ VÀNG TẦM SOÁT")
    if st.session_state.history_log:
        st.table(pd.DataFrame(st.session_state.history_log))
    else:
        st.info("Chưa có con cá nào được lưu.")

# --- FOOTER ---
st.markdown("---")
st.caption("🚀 Bể Lọc Siêu Cấp 2026 - Tư duy Trường Money & A7 - Built with Passion")