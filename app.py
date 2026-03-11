import random
﻿import random
from datetime import datetime

import pandas as pd


# -------------------------------
# DỮ LIỆU & TÍNH TOÁN CÓ CACHE
# Dá»® LIá»†U & TÃNH TOÃN CÃ“ CACHE
# -------------------------------
@st.cache_data(ttl=600, show_spinner=False)
def load_ticker_data(ticker: str) -> pd.DataFrame:
    """Hàm máy bơm: hút dữ liệu giá của 1 mã từ Yahoo Finance."""
    """HÃ m mÃ¡y bÆ¡m: hÃºt dá»¯ liá»‡u giÃ¡ cá»§a 1 mÃ£ tá»« Yahoo Finance."""
    data = yf.download(f"{ticker}.VN", period="150d", progress=False)
    if data.empty:
        return pd.DataFrame()
@st.cache_data(ttl=600, show_spinner=False)
def load_all_ticker_data(tickers: list[str]) -> dict[str, pd.DataFrame]:
    """
    Tải gộp nhiều mã cho Radar, flatten ngay về dict để tránh xs() từng vòng lặp.
    Giảm đáng kể overhead MultiIndex mỗi lần duyệt.
    Táº£i gá»™p nhiá»u mÃ£ cho Radar, flatten ngay vá» dict Ä‘á»ƒ trÃ¡nh xs() tá»«ng vÃ²ng láº·p.
    Giáº£m Ä‘Ã¡ng ká»ƒ overhead MultiIndex má»—i láº§n duyá»‡t.
    """
    tickers_with_suffix = [f"{t}.VN" for t in tickers]
    raw = yf.download(tickers_with_suffix, period="150d", progress=False, group_by="ticker")

@st.cache_data(ttl=600, show_spinner=False)
def load_vni_data() -> pd.DataFrame:
    """Tải VN-Index với cache để tránh gọi lại mỗi rerun."""
    """Táº£i VN-Index vá»›i cache Ä‘á»ƒ trÃ¡nh gá»i láº¡i má»—i rerun."""
    data = yf.download("^VNI", period="150d", progress=False)
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)


def compute_rsi_pro(data: pd.Series, window: int = 14) -> pd.Series:
    """Tính RSI (vector hóa)."""
    """TÃ­nh RSI (vector hÃ³a)."""
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    return 100 - (100 / (1 + rs))


# --- 1. MÁY BƠM LINH ĐƠN (Sử dụng File Master 50 Cột) ---
# --- 1. MÃY BÆ M LINH ÄÆ N (Sá»­ dá»¥ng File Master 50 Cá»™t) ---
@st.cache_data(ttl=3600, show_spinner=False)
def load_vietstock_data() -> pd.DataFrame:
    """Hút linh đơn 50 cột đã luyện sạch - Siêu nhanh, siêu gọn"""
    # Link file Master bro đã up lên Github
    """HÃºt linh Ä‘Æ¡n 50 cá»™t Ä‘Ã£ luyá»‡n sáº¡ch - SiÃªu nhanh, siÃªu gá»n"""
    # Link file Master bro Ä‘Ã£ up lÃªn Github
    url = "https://github.com/DAOHUUDAT/Be-Loc-Sieu-Cap/raw/refs/heads/main/data/BE_LOC_MASTER_50.xlsx"
    try:
        # Nếu file trên Github là Excel dùng read_excel, nếu là csv dùng read_csv
        # Ở đây tôi mặc định bro dùng Excel như tên file
        # Náº¿u file trÃªn Github lÃ  Excel dÃ¹ng read_excel, náº¿u lÃ  csv dÃ¹ng read_csv
        # á»ž Ä‘Ã¢y tÃ´i máº·c Ä‘á»‹nh bro dÃ¹ng Excel nhÆ° tÃªn file
        df = pd.read_excel(url)
        # Làm sạch tên cột để tránh lỗi khoảng trắng
        # LÃ m sáº¡ch tÃªn cá»™t Ä‘á»ƒ trÃ¡nh lá»—i khoáº£ng tráº¯ng
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"❌ Lỗi hút linh đơn: {e}")
        st.error(f"âŒ Lá»—i hÃºt linh Ä‘Æ¡n: {e}")
        return pd.DataFrame()

# Nạp dữ liệu Master
# Náº¡p dá»¯ liá»‡u Master
df_master = load_vietstock_data()
TICKERS = df_master["Mã CK"].tolist() if not df_master.empty else []
TICKERS = df_master["MÃ£ CK"].tolist() if not df_master.empty else []

# -------------------------------
# 1. CẤU HÌNH HỆ THỐNG GIAO DIỆN
# 1. Cáº¤U HÃŒNH Há»† THá»NG GIAO DIá»†N
# -------------------------------
st.set_page_config(page_title="HÃY CHỌN CÁ ĐÚNG v6.3.15", layout="wide", initial_sidebar_state="expanded")
st.set_page_config(page_title="HÃƒY CHá»ŒN CÃ ÄÃšNG v6.3.15", layout="wide", initial_sidebar_state="expanded")

st.markdown(
    """
if "ticker_input_analysis" not in st.session_state:
    st.session_state.ticker_input_analysis = st.session_state.selected_ticker

# --- TỪ ĐIỂN VIỆT HÓA BCTC (để dành dùng sau) ---
# --- Tá»ª ÄIá»‚N VIá»†T HÃ“A BCTC (Ä‘á»ƒ dÃ nh dÃ¹ng sau) ---
DICTIONARY_BCTC = {
    "Total Revenue": "Tổng Doanh thu",
    "Operating Revenue": "Doanh thu hoạt động",
    "Cost Of Revenue": "Giá vốn hàng bán",
    "Gross Profit": "Lợi nhuận gộp",
    "Operating Expense": "Chi phí hoạt động",
    "Selling General And Administration": "Chi phí bán hàng & QLDN",
    "Selling And Marketing Expense": "Chi phí bán hàng & Marketing",
    "General And Administrative Expense": "Chi phí quản lý doanh nghiệp",
    "Rent Expense Supplemental": "Chi phí thuê bổ sung",
    "Rent And Landing Fees": "Chi phí thuê & phí bãi",
    "Depreciation And Amortization In Income Statement": "Khấu hao trong BCKQKD",
    "Depreciation Income Statement": "Khấu hao (BCKQKD)",
    "Operating Income": "Lợi nhuận từ HĐKD",
    "Total Operating Income As Reported": "Tổng LN hoạt động (Báo cáo)",
    "Total Expenses": "Tổng chi phí",
    "Other Non Operating Income Expenses": "Thu nhập/Chi phí phi hoạt động khác",
    "Special Income Charges": "Chi phí thu nhập đặc biệt",
    "Other Special Charges": "Chi phí đặc biệt khác",
    "Net Interest Income": "Thu nhập lãi thuần",
    "Interest Income": "Thu nhập lãi vay",
    "Interest Expense": "Chi phí lãi vay",
    "Net Non Operating Interest Income Expense": "Thu nhập lãi phi hoạt động thuần",
    "Total Other Finance Cost": "Tổng chi phí tài chính khác",
    "Pretax Income": "Lợi nhuận trước thuế",
    "Tax Provision": "Dự phòng thuế",
    "Net Income": "Lợi nhuận ròng",
    "Net Income Common Stockholders": "LN ròng dành cho CĐ phổ thông",
    "Normalized Income": "Lợi nhuận điều chỉnh (Normalized)",
    "Basic EPS": "EPS cơ bản",
    "Diluted EPS": "EPS pha loãng",
    "Total Revenue": "Tá»•ng Doanh thu",
    "Operating Revenue": "Doanh thu hoáº¡t Ä‘á»™ng",
    "Cost Of Revenue": "GiÃ¡ vá»‘n hÃ ng bÃ¡n",
    "Gross Profit": "Lá»£i nhuáº­n gá»™p",
    "Operating Expense": "Chi phÃ­ hoáº¡t Ä‘á»™ng",
    "Selling General And Administration": "Chi phÃ­ bÃ¡n hÃ ng & QLDN",
    "Selling And Marketing Expense": "Chi phÃ­ bÃ¡n hÃ ng & Marketing",
    "General And Administrative Expense": "Chi phÃ­ quáº£n lÃ½ doanh nghiá»‡p",
    "Rent Expense Supplemental": "Chi phÃ­ thuÃª bá»• sung",
    "Rent And Landing Fees": "Chi phÃ­ thuÃª & phÃ­ bÃ£i",
    "Depreciation And Amortization In Income Statement": "Kháº¥u hao trong BCKQKD",
    "Depreciation Income Statement": "Kháº¥u hao (BCKQKD)",
    "Operating Income": "Lá»£i nhuáº­n tá»« HÄKD",
    "Total Operating Income As Reported": "Tá»•ng LN hoáº¡t Ä‘á»™ng (BÃ¡o cÃ¡o)",
    "Total Expenses": "Tá»•ng chi phÃ­",
    "Other Non Operating Income Expenses": "Thu nháº­p/Chi phÃ­ phi hoáº¡t Ä‘á»™ng khÃ¡c",
    "Special Income Charges": "Chi phÃ­ thu nháº­p Ä‘áº·c biá»‡t",
    "Other Special Charges": "Chi phÃ­ Ä‘áº·c biá»‡t khÃ¡c",
    "Net Interest Income": "Thu nháº­p lÃ£i thuáº§n",
    "Interest Income": "Thu nháº­p lÃ£i vay",
    "Interest Expense": "Chi phÃ­ lÃ£i vay",
    "Net Non Operating Interest Income Expense": "Thu nháº­p lÃ£i phi hoáº¡t Ä‘á»™ng thuáº§n",
    "Total Other Finance Cost": "Tá»•ng chi phÃ­ tÃ i chÃ­nh khÃ¡c",
    "Pretax Income": "Lá»£i nhuáº­n trÆ°á»›c thuáº¿",
    "Tax Provision": "Dá»± phÃ²ng thuáº¿",
    "Net Income": "Lá»£i nhuáº­n rÃ²ng",
    "Net Income Common Stockholders": "LN rÃ²ng dÃ nh cho CÄ phá»• thÃ´ng",
    "Normalized Income": "Lá»£i nhuáº­n Ä‘iá»u chá»‰nh (Normalized)",
    "Basic EPS": "EPS cÆ¡ báº£n",
    "Diluted EPS": "EPS pha loÃ£ng",
}

# -------------------------------
# 2. SIDEBAR: TRI KỶ & CẨM NANG
# 2. SIDEBAR: TRI Ká»¶ & Cáº¨M NANG
# -------------------------------
with st.sidebar:
    img_url = "https://github.com/DAOHUUDAT/Be-Loc-Sieu-Cap/blob/main/anh-tri-ky.jpg?raw=true"
        unsafe_allow_html=True,
    )

    st.header("🎮 ĐÀI CHỈ HUY")
    t_input = st.text_input("🔍 SOI MÃ CÁ", "VNI").upper()
    st.header("ðŸŽ® ÄÃ€I CHá»ˆ HUY")
    t_input = st.text_input("ðŸ” SOI MÃƒ CÃ", "VNI").upper()
    st.divider()

    st.header("📓 CẨM NANG")
    with st.expander("📖 Giải mã thông số", expanded=True):
        st.markdown("### 🚀 Hệ sinh thái Cá:")
        st.write("- **SIÊU CÁ:** hội tụ 3 yếu tố: Giá > MA20 + Vol đột biến (>120%) + Sức mạnh RS khỏe hơn VN-Index.")
        st.write("- **Cá Lớn 🐋:** Xu hướng tăng bền vững (Giá nằm trên cả MA20 và MA50).")
        st.write("- **Cá Đang Lớn 🐡:** Giai đoạn chuyển mình, vừa chớm vượt MA20.")
        st.write("- **Cá Nhỏ 🐟:** Dưới trung bình, dòng tiền yếu - Tạm bỏ qua.")
        st.markdown("### 🌩️ Trạng thái dòng nước:")
        st.write("- **💪 Khỏe:** Sức mạnh tương đối (RS) dương - cá đang bơi khỏe hơn thị trường chung.")
        st.write("- **🌊 Sóng:** Vol > 150% trung bình 20 phiên - dấu hiệu 'cá mập' đang đẩy giá.")
        st.write("- **🌩️ Nhiệt độ (RSI):** Nóng (>70) dễ điều chỉnh, Lạnh (<30) quá bán.")
    st.header("ðŸ““ Cáº¨M NANG")
    with st.expander("ðŸ“– Giáº£i mÃ£ thÃ´ng sá»‘", expanded=True):
        st.markdown("### ðŸš€ Há»‡ sinh thÃ¡i CÃ¡:")
        st.write("- **SIÃŠU CÃ:** há»™i tá»¥ 3 yáº¿u tá»‘: GiÃ¡ > MA20 + Vol Ä‘á»™t biáº¿n (>120%) + Sá»©c máº¡nh RS khá»e hÆ¡n VN-Index.")
        st.write("- **CÃ¡ Lá»›n ðŸ‹:** Xu hÆ°á»›ng tÄƒng bá»n vá»¯ng (GiÃ¡ náº±m trÃªn cáº£ MA20 vÃ  MA50).")
        st.write("- **CÃ¡ Äang Lá»›n ðŸ¡:** Giai Ä‘oáº¡n chuyá»ƒn mÃ¬nh, vá»«a chá»›m vÆ°á»£t MA20.")
        st.write("- **CÃ¡ Nhá» ðŸŸ:** DÆ°á»›i trung bÃ¬nh, dÃ²ng tiá»n yáº¿u - Táº¡m bá» qua.")
        st.markdown("### ðŸŒ©ï¸ Tráº¡ng thÃ¡i dÃ²ng nÆ°á»›c:")
        st.write("- **ðŸ’ª Khá»e:** Sá»©c máº¡nh tÆ°Æ¡ng Ä‘á»‘i (RS) dÆ°Æ¡ng - cÃ¡ Ä‘ang bÆ¡i khá»e hÆ¡n thá»‹ trÆ°á»ng chung.")
        st.write("- **ðŸŒŠ SÃ³ng:** Vol > 150% trung bÃ¬nh 20 phiÃªn - dáº¥u hiá»‡u 'cÃ¡ máº­p' Ä‘ang Ä‘áº©y giÃ¡.")
        st.write("- **ðŸŒ©ï¸ Nhiá»‡t Ä‘á»™ (RSI):** NÃ³ng (>70) dá»… Ä‘iá»u chá»‰nh, Láº¡nh (<30) quÃ¡ bÃ¡n.")
        st.divider()
        st.markdown(f"### 💎 Mổ xẻ chi tiết: {t_input}")
        st.write("- **🧭 Niềm tin (%):** đo sự đồng thuận giữa tăng trưởng doanh thu và vị thế giá kỹ thuật.")
        st.write("- **💰 Định giá 3 kịch bản:** Thận trọng / Cơ sở / Phi thường.")
        st.write("- **📈 Tuyệt kỹ Ichimoku:** Mây, Tenkan, Kijun giữ nguyên ý nghĩa.")
        st.write("- **🍱 Chiến thuật 'Thức ăn':** khoảng cách về MA20, kiểm tra % dư địa.")
        st.markdown(f"### ðŸ’Ž Má»• xáº» chi tiáº¿t: {t_input}")
        st.write("- **ðŸ§­ Niá»m tin (%):** Ä‘o sá»± Ä‘á»“ng thuáº­n giá»¯a tÄƒng trÆ°á»Ÿng doanh thu vÃ  vá»‹ tháº¿ giÃ¡ ká»¹ thuáº­t.")
        st.write("- **ðŸ’° Äá»‹nh giÃ¡ 3 ká»‹ch báº£n:** Tháº­n trá»ng / CÆ¡ sá»Ÿ / Phi thÆ°á»ng.")
        st.write("- **ðŸ“ˆ Tuyá»‡t ká»¹ Ichimoku:** MÃ¢y, Tenkan, Kijun giá»¯ nguyÃªn Ã½ nghÄ©a.")
        st.write("- **ðŸ± Chiáº¿n thuáº­t 'Thá»©c Äƒn':** khoáº£ng cÃ¡ch vá» MA20, kiá»ƒm tra % dÆ° Ä‘á»‹a.")
    st.divider()
    QUOTES = [
        "“Trong đầu tư, thứ đắt đỏ nhất là sự thiếu kiên nhẫn.”",
        "“Hãy mua con cá khỏe nhất trong dòng nước yếu nhất.”",
        "“Đừng cố bắt cá khi đại dương đang có bão lớn.”",
        "“Siêu cá không xuất hiện mỗi ngày, hãy kiên nhẫn đợi điểm nổ.”",
        "“Kỷ luật là thứ tách biệt ngư dân chuyên nghiệp và kẻ đi dạo.”",
        "“Giá là thứ bạn trả, giá trị là thứ con cá mang lại.”",
        "â€œTrong Ä‘áº§u tÆ°, thá»© Ä‘áº¯t Ä‘á» nháº¥t lÃ  sá»± thiáº¿u kiÃªn nháº«n.â€",
        "â€œHÃ£y mua con cÃ¡ khá»e nháº¥t trong dÃ²ng nÆ°á»›c yáº¿u nháº¥t.â€",
        "â€œÄá»«ng cá»‘ báº¯t cÃ¡ khi Ä‘áº¡i dÆ°Æ¡ng Ä‘ang cÃ³ bÃ£o lá»›n.â€",
        "â€œSiÃªu cÃ¡ khÃ´ng xuáº¥t hiá»‡n má»—i ngÃ y, hÃ£y kiÃªn nháº«n Ä‘á»£i Ä‘iá»ƒm ná»•.â€",
        "â€œKá»· luáº­t lÃ  thá»© tÃ¡ch biá»‡t ngÆ° dÃ¢n chuyÃªn nghiá»‡p vÃ  káº» Ä‘i dáº¡o.â€",
        "â€œGiÃ¡ lÃ  thá»© báº¡n tráº£, giÃ¡ trá»‹ lÃ  thá»© con cÃ¡ mang láº¡i.â€",
    ]
    st.info(f"💡 {random.choice(QUOTES)}")
    st.info(f"ðŸ’¡ {random.choice(QUOTES)}")
    st.divider()
    st.caption(
        """
        ⚠️ **MIỄN TRỪ TRÁCH NHIỆM:** Mọi dữ liệu & phân tích chỉ mang tính tham khảo, không phải khuyến nghị đầu tư.
        Đầu tư luôn tiềm ẩn rủi ro. Hãy tự tìm hiểu và quản trị rủi ro cá nhân.
        âš ï¸ **MIá»„N TRá»ª TRÃCH NHIá»†M:** Má»i dá»¯ liá»‡u & phÃ¢n tÃ­ch chá»‰ mang tÃ­nh tham kháº£o, khÃ´ng pháº£i khuyáº¿n nghá»‹ Ä‘áº§u tÆ°.
        Äáº§u tÆ° luÃ´n tiá»m áº©n rá»§i ro. HÃ£y tá»± tÃ¬m hiá»ƒu vÃ  quáº£n trá»‹ rá»§i ro cÃ¡ nhÃ¢n.
        """
    )

st.title("🚀 Bể Lọc v6.3.15: HÃY CHỌN CÁ ĐÚNG")
st.title("ðŸš€ Bá»ƒ Lá»c v6.3.15: HÃƒY CHá»ŒN CÃ ÄÃšNG")

# ------------------------------------
# 3. TRẠM QUAN TRẮC ĐẠI DƯƠNG (VN-INDEX)
# 3. TRáº M QUAN TRáº®C Äáº I DÆ¯Æ NG (VN-INDEX)
# ------------------------------------
inf_factor = 1.0
v_c = 1200.0
        if len(vni) >= 20:
            vni_perf_base = vni["Close"].iloc[-20]
        st.info(
            f"🌊 Đại Dương: {'🟢 THẢ LƯỚI (Sóng Thuận)' if v_c > vsa else '🔴 ĐÁNH KẸO (Sóng Nghịch)'} | Co giãn: {inf_factor}x"
            f"ðŸŒŠ Äáº¡i DÆ°Æ¡ng: {'ðŸŸ¢ THáº¢ LÆ¯á»šI (SÃ³ng Thuáº­n)' if v_c > vsa else 'ðŸ”´ ÄÃNH Káº¸O (SÃ³ng Nghá»‹ch)'} | Co giÃ£n: {inf_factor}x"
        )
    except Exception:
        pass

# -------------------------------
# 4. HỆ THỐNG TABS
# 4. Há»† THá»NG TABS
# -------------------------------
tab_radar, tab_analysis, tab_bctc, tab_history = st.tabs(
    ["🎯 RADAR ELITE", "💎 CHI TIẾT SIÊU CÁ", "📊 MỔ XẺ BCTC", "📓 SỔ VÀNG"]
    ["ðŸŽ¯ RADAR ELITE", "ðŸ’Ž CHI TIáº¾T SIÃŠU CÃ", "ðŸ“Š Má»” Xáºº BCTC", "ðŸ““ Sá»” VÃ€NG"]
)

with tab_radar:
    st.subheader("🤖 Top 20 SIÊU CÁ (Hệ thống Radar)")
    st.subheader("ðŸ¤– Top 20 SIÃŠU CÃ (Há»‡ thá»‘ng Radar)")
    elite_20 = ["DGC", "MWG", "FPT", "TCB", "SSI", "HPG", "GVR", "CTR", "DBC", "VNM", "STB", "MBB", "ACB", "KBC", "VGC", "PVS", "PVD", "ANV", "VHC", "REE"]
    radar_list = []

    all_data = load_all_ticker_data(elite_20)
    with st.spinner("Đang quét tín hiệu từ đại dương..."):
    with st.spinner("Äang quÃ©t tÃ­n hiá»‡u tá»« Ä‘áº¡i dÆ°Æ¡ng..."):
        for tk in elite_20:
            d = all_data.get(tk, pd.DataFrame())
            if d.empty:
            is_stronger = stock_perf > vni_perf

            curr_rsi = compute_rsi_pro(d["Close"]).iloc[-1]
            temp = "🔥 Nóng" if curr_rsi > 70 else "❄️ Lạnh" if curr_rsi < 30 else "🌤️ Êm"
            temp = "ðŸ”¥ NÃ³ng" if curr_rsi > 70 else "â„ï¸ Láº¡nh" if curr_rsi < 30 else "ðŸŒ¤ï¸ ÃŠm"

            if p_c > ma20 and v_now > v_avg * 1.5 and is_stronger:
                loai_ca, priority = "🚀 SIÊU CÁ", 1
                loai_ca, priority = "ðŸš€ SIÃŠU CÃ", 1
            elif p_c > ma20 and p_c > ma50:
                loai_ca, priority = "Cá Lớn 🐋", 2
                loai_ca, priority = "CÃ¡ Lá»›n ðŸ‹", 2
            elif p_c > ma20:
                loai_ca, priority = "Cá Đang Lớn 🐡", 3
                loai_ca, priority = "CÃ¡ Äang Lá»›n ðŸ¡", 3
            else:
                loai_ca, priority = "Cá Nhỏ 🐟", 4
                loai_ca, priority = "CÃ¡ Nhá» ðŸŸ", 4

            radar_list.append(
                {
                    "Mã": tk,
                    "Giá": f"{p_c:,.0f}",
                    "Sóng": "🌊 Mạnh" if v_now > v_avg * 1.5 else "☕ Lặng",
                    "Nhiệt độ": temp,
                    "Đại Dương": "💪 Khỏe" if is_stronger else "🐌 Yếu",
                    "Loại": loai_ca,
                    "Thức ăn": f"{((ma20 / p_c) - 1) * 100:+.1f}%" if p_c < ma20 else "✅ Đang no",
                    "MÃ£": tk,
                    "GiÃ¡": f"{p_c:,.0f}",
                    "SÃ³ng": "ðŸŒŠ Máº¡nh" if v_now > v_avg * 1.5 else "â˜• Láº·ng",
                    "Nhiá»‡t Ä‘á»™": temp,
                    "Äáº¡i DÆ°Æ¡ng": "ðŸ’ª Khá»e" if is_stronger else "ðŸŒ Yáº¿u",
                    "Loáº¡i": loai_ca,
                    "Thá»©c Äƒn": f"{((ma20 / p_c) - 1) * 100:+.1f}%" if p_c < ma20 else "âœ… Äang no",
                    "priority": priority,
                    "RS_Raw": stock_perf - vni_perf,
                }

    if selection and len(selection.selection.rows) > 0:
        selected_idx = selection.selection.rows[0]
        picked = df_radar.iloc[selected_idx]["Mã"]
        picked = df_radar.iloc[selected_idx]["MÃ£"]
        st.session_state.selected_ticker = picked
        st.session_state.ticker_input_analysis = picked  # sync với ô nhập phân tích
        st.toast(f"🎯 Đã khóa mục tiêu: {picked}", icon="🚀")
        st.session_state.ticker_input_analysis = picked  # sync vá»›i Ã´ nháº­p phÃ¢n tÃ­ch
        st.toast(f"ðŸŽ¯ ÄÃ£ khÃ³a má»¥c tiÃªu: {picked}", icon="ðŸš€")
        st.rerun()

with tab_analysis:
    if st.session_state.get("ticker_input_analysis") != target:
        st.session_state.ticker_input_analysis = target

    t_input = st.text_input("Nhập mã cá muốn mổ xẻ:", value=st.session_state.ticker_input_analysis, key="ticker_input_analysis").upper()
    t_input = st.text_input("Nháº­p mÃ£ cÃ¡ muá»‘n má»• xáº»:", value=st.session_state.ticker_input_analysis, key="ticker_input_analysis").upper()

    if t_input != st.session_state.selected_ticker:
        st.session_state.selected_ticker = t_input
    try:
        s_df = load_ticker_data(t_input)
        if s_df.empty:
            st.error(f"Chưa lấy được dữ liệu cho {t_input}.")
            st.error(f"ChÆ°a láº¥y Ä‘Æ°á»£c dá»¯ liá»‡u cho {t_input}.")
            st.stop()

        t_obj = yf.Ticker(f"{t_input}.VN")
            except Exception:
                pass

        st.markdown(f"### 🧭 Niềm tin {t_input}: {trust}%")
        st.markdown(f"### ðŸ§­ Niá»m tin {t_input}: {trust}%")
        c_p, c1, c2, c3 = st.columns(4)
        p_base = curr_p * (1 + rev_growth) * inf_factor
        c_p.metric("📍 GIÁ HIỆN TẠI", f"{curr_p:,.0f}")
        c1.metric("🐢 Thận trọng", f"{curr_p * (1 + rev_growth * 0.4) * inf_factor:,.0f}")
        c2.metric("🏰 Cơ sở", f"{p_base:,.0f}")
        c3.metric("🚀 Phi thường", f"{curr_p * (1 + rev_growth * 2) * inf_factor:,.0f}")
        c_p.metric("ðŸ“ GIÃ HIá»†N Táº I", f"{curr_p:,.0f}")
        c1.metric("ðŸ¢ Tháº­n trá»ng", f"{curr_p * (1 + rev_growth * 0.4) * inf_factor:,.0f}")
        c2.metric("ðŸ° CÆ¡ sá»Ÿ", f"{p_base:,.0f}")
        c3.metric("ðŸš€ Phi thÆ°á»ng", f"{curr_p * (1 + rev_growth * 2) * inf_factor:,.0f}")

        st.subheader("📊 Sức khỏe tài chính 5 Quý gần nhất (Tỷ VNĐ)")
        st.subheader("ðŸ“Š Sá»©c khá»e tÃ i chÃ­nh 5 QuÃ½ gáº§n nháº¥t (Tá»· VNÄ)")
        if not fin_q.empty:
            q_rev = (fin_q.loc["Total Revenue"].iloc[:5][::-1]) / 1e9 if "Total Revenue" in fin_q.index else pd.Series(dtype=float)
            if "Net Income" in fin_q.index:
                    go.Bar(
                        x=q_net.index.astype(str),
                        y=q_net,
                        name="Lợi nhuận",
                        name="Lá»£i nhuáº­n",
                        marker_color="#FFD700",
                        text=q_net.apply(lambda x: f"{x:,.1f}"),
                        textposition="auto",
                    height=350,
                    margin=dict(l=0, r=0, t=30, b=0),
                    template="plotly_white",
                    yaxis_title="Tỷ VNĐ",
                    yaxis_title="Tá»· VNÄ",
                )
                st.plotly_chart(fig_fin, use_container_width=True)

        st.subheader(f"📈 Phân tích kỹ thuật {t_input}")
        st.subheader(f"ðŸ“ˆ PhÃ¢n tÃ­ch ká»¹ thuáº­t {t_input}")
        s_df["tk"] = (s_df["High"].rolling(9).max() + s_df["Low"].rolling(9).min()) / 2
        s_df["kj"] = (s_df["High"].rolling(26).max() + s_df["Low"].rolling(26).min()) / 2
        s_df["sa"] = ((s_df["tk"] + s_df["kj"]) / 2).shift(26)
        s_df["Vol_Avg"] = s_df["Volume"].rolling(20).mean()

        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.7, 0.3])
        fig.add_trace(go.Candlestick(x=s_df.index, open=s_df["Open"], high=s_df["High"], low=s_df["Low"], close=s_df["Close"], name="Giá"), row=1, col=1)
        fig.add_trace(go.Candlestick(x=s_df.index, open=s_df["Open"], high=s_df["High"], low=s_df["Low"], close=s_df["Close"], name="GiÃ¡"), row=1, col=1)
        fig.add_trace(go.Scatter(x=s_df.index, y=s_df["sa"], line=dict(width=0), showlegend=False), row=1, col=1)
        fig.add_trace(go.Scatter(x=s_df.index, y=s_df["sb"], line=dict(width=0), fill="tonexty", fillcolor="rgba(0, 150, 255, 0.1)", name="Mây"), row=1, col=1)
        fig.add_trace(go.Scatter(x=s_df.index, y=s_df["sb"], line=dict(width=0), fill="tonexty", fillcolor="rgba(0, 150, 255, 0.1)", name="MÃ¢y"), row=1, col=1)
        fig.add_trace(go.Scatter(x=s_df.index, y=s_df["tk"], line=dict(color="#FF33CC", width=2), name="Tenkan"), row=1, col=1)
        fig.add_trace(go.Scatter(x=s_df.index, y=s_df["kj"], line=dict(color="#FFD700", width=2), name="Kijun"), row=1, col=1)

        fig.update_layout(height=500, xaxis_rangeslider_visible=False, template="plotly_white", margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig, use_container_width=True)

        if st.button(f"📌 Lưu {t_input} vào Sổ Vàng"):
            st.session_state.history_log.append({"Mã": t_input, "Giá": f"{curr_p:,.0f}", "Ngày": datetime.now().strftime("%d/%m")})
        if st.button(f"ðŸ“Œ LÆ°u {t_input} vÃ o Sá»• VÃ ng"):
            st.session_state.history_log.append({"MÃ£": t_input, "GiÃ¡": f"{curr_p:,.0f}", "NgÃ y": datetime.now().strftime("%d/%m")})
            st.rerun()
    except Exception:
        st.error(f"Đang tạm soát mã cá {t_input}...")
        st.error(f"Äang táº¡m soÃ¡t mÃ£ cÃ¡ {t_input}...")

with tab_bctc:
    st.subheader(f"📊 Mổ xẻ nội tạng Cá: {t_input}")

    uploaded_file = st.file_uploader(f"📂 Tải lên BCTC PDF của {t_input}", type=["pdf"])
    if uploaded_file:
        st.success(f"✅ Đã nhận file. Gemini sẵn sàng mổ xẻ mã {t_input}!")

    st.divider()

    if t_input and not vietstock_db.empty:
        fish_data = vietstock_db[vietstock_db["Mã CK"] == t_input]

        if not fish_data.empty:
            row = fish_data.iloc[0]

            def find_col(keyword):
                cols = [c for c in vietstock_db.columns if keyword.lower() in str(c).lower()]
                return cols[0] if cols else None

        # --- TRONG TAB CHI TIẾT: PHÂN TÍCH NỘI TẠNG CÁ ---
    if not df_master.empty:
        row = df_master[df_master['Mã CK'] == t_input].iloc[0]
    
        # 1. Đo lường sức khỏe (Metrics)
        c1, c2, c3 = st.columns(3)
    
        # Giờ gọi tên cột trực tiếp vì đã chuẩn hóa trong file Master
        revenue = row.get('Doanh thu thuần', 0)
        profit = row.get('Lợi nhuận sau thuế của cổ đông của Công ty mẹ', 0)
        eps = row.get('Lãi cơ bản trên cổ phiếu', 0)
    
        c1.metric("Doanh thu (Tỷ)", f"{revenue/1e9:,.1f}")
        c2.metric("Lợi nhuận (Tỷ)", f"{profit/1e9:,.1f}")
        c3.metric("EPS (VND)", f"{eps:,.0f}")

            with col_fa1:
                st.write("**📑 Thông số tài chính cốt lõi (Từ file Excel):**")
                summary_data = {
                    "Chỉ số": ["Doanh thu", "Lợi nhuận sau thuế", "Hàng tồn kho", "Tiền mặt"],
                    "Giá trị (VND)": [
                        f"{row[col_rev]:,.0f}" if col_rev else "N/A",
                        f"{row[col_profit]:,.0f}" if col_profit else "N/A",
                        f"{row[col_inventory]:,.0f}" if col_inventory else "N/A",
                        f"{row[col_cash]:,.0f}" if col_cash else "N/A",
                    ],
                }
                st.table(pd.DataFrame(summary_data))

            with col_fa2:
                st.write("**🏆 Đánh giá nhanh:**")
                if col_profit and col_rev:
                    val_profit = row[col_profit]
                    val_rev = row[col_rev]
                    st.metric("Lợi nhuận", f"{val_profit/1e9:,.2f} Tỷ")
                    net_margin = (val_profit / val_rev) * 100 if val_rev > 0 else 0
                    st.metric("Biên Lợi Nhuận Ròng", f"{net_margin:.1f}%")

                    if val_profit > 0:
                        st.success("🌟 Cá có lãi, nội tạng tốt!")
                    else:
                        st.error("⚠️ Cá đang sụt cân (Lỗ)")

            st.divider()
            st.subheader("🧠 Phân tích chuyên sâu (Tầm nhìn A7)")
            c1, c2 = st.columns(2)
            
            # Lấy dữ liệu trực tiếp
            inventory = row.get("Hàng tồn kho", 0)
            cash = row.get("Tiền và các khoản tương đương tiền", 0)
            # Tính tổng nợ vay
            debt = row.get("Vay và nợ thuê tài chính ngắn hạn", 0) + row.get("Vay và nợ thuê tài chính dài hạn", 0)

            c1.info(f"📦 **Của để dành (Tồn kho):** {inventory/1e9:,.1f} Tỷ")
            c2.info(f"💰 **Sức mạnh tiền mặt:** {cash/1e9:,.1f} Tỷ")

            # Cảnh báo nợ vay - Tính năng mới cho v7.0
            if debt > cash:
                st.warning(f"⚠️ Nợ vay ({debt/1e9:,.1f} Tỷ) > Tiền mặt. Cá đang dùng đòn bẩy cao!")
            else:
                st.success(f"✅ Tài chính lành mạnh: Tiền mặt đủ bao nợ.")

            st.info("💡 Kiểm tra xem 'Hàng tồn kho' có phải là các dự án sắp mở bán không. Đó là ngòi nổ cho SIÊU CÁ!")

with tab_bctc:
    st.subheader(f"📊 Mổ xẻ nội tạng Cá: {t_input}")

    uploaded_file = st.file_uploader(f"📂 Tải lên BCTC PDF của {t_input}", type=["pdf"])
    if uploaded_file:
        st.success(f"✅ Đã nhận file. Gemini sẵn sàng mổ xẻ mã {t_input}!")

    st.divider()

    # --- TRONG TAB CHI TIẾT: PHÂN TÍCH NỘI TẠNG CÁ ---
    if not df_master.empty and t_input:
        fish_data = df_master[df_master["MÃ£ CK"] == t_input]
        if fish_data.empty:
            st.info(f"Chưa có dữ liệu cơ bản cho {t_input} trong file Master.")
        else:
            row = fish_data.iloc[0]

            c1, c2, c3 = st.columns(3)
            revenue = float(row.get("Doanh thu thuần", 0) or 0)
            profit = float(row.get("Lợi nhuận sau thuế của cổ đông của Công ty mẹ", 0) or 0)
            eps = float(row.get("Lãi cơ bản trên cổ phiếu", 0) or 0)

            c1.metric("Doanh thu (Tỷ)", f"{revenue/1e9:,.1f}")
            c2.metric("Lợi nhuận (Tỷ)", f"{profit/1e9:,.1f}")
            c3.metric("EPS (VND)", f"{eps:,.0f}")

            col_fa1, col_fa2 = st.columns(2)
            with col_fa1:
                st.write("**📑 Thông số tài chính cốt lõi (từ file Master):**")
                summary_data = {
                    "Chỉ số": ["Doanh thu", "Lợi nhuận sau thuế", "Hàng tồn kho", "Tiền mặt"],
                    "Giá trị (VND)": [
                        f"{revenue:,.0f}",
                        f"{profit:,.0f}",
                        f"{row.get('Hàng tồn kho', 0):,.0f}",
                        f"{row.get('Tiền và các khoản tương đương tiền', 0):,.0f}",
                    ],
                }
                st.table(pd.DataFrame(summary_data))

            with col_fa2:
                st.write("**🏆 Đánh giá nhanh:**")
                net_margin = (profit / revenue * 100) if revenue else 0
                st.metric("Biên lợi nhuận ròng", f"{net_margin:.1f}%")
                if profit > 0:
                    st.success("🌟 Cá có lãi, nội tạng ổn.")
                else:
                    st.error("⚠️ Cá đang lỗ, cần theo dõi.")

            st.divider()
            st.subheader("🧠 Phân tích chuyên sâu (Tầm nhìn A7)")
            c1, c2 = st.columns(2)
            inventory = float(row.get("Hàng tồn kho", 0) or 0)
            cash = float(row.get("Tiền và các khoản tương đương tiền", 0) or 0)
            debt_short = float(row.get("Vay và nợ thuê tài chính ngắn hạn", 0) or 0)
            debt_long = float(row.get("Vay và nợ thuê tài chính dài hạn", 0) or 0)
            debt = debt_short + debt_long

            c1.info(f"📦 Tồn kho: {inventory/1e9:,.1f} Tỷ")
            c2.info(f"💰 Tiền mặt: {cash/1e9:,.1f} Tỷ")

            if debt > cash:
                st.warning(f"⚠️ Nợ vay ({debt/1e9:,.1f} Tỷ) vượt tiền mặt.")
            else:
                st.success("✅ Tiền mặt đủ bao nợ.")

            st.info("💡 Kiểm tra xem 'Hàng tồn kho' có phải dự án sắp mở bán không; đây có thể là điểm kích nổ.")

with tab_history:
    st.subheader("📓 DANH SÁCH CÁ ĐÃ TẦM SOÁT")
    st.subheader("ðŸ““ DANH SÃCH CÃ ÄÃƒ Táº¦M SOÃT")
    if st.session_state.history_log:
        st.table(pd.DataFrame(st.session_state.history_log))
        st.info(
            """
            **📌 Ghi chú cho Ngư dân:**
            * **Giá lưu:** mức giá tại thời điểm đưa cá vào tầm ngắm.
            * **Kỷ luật:** Chỉ nên giữ tối đa 5-7 mã trong Sổ Vàng để tập trung nguồn lực.
            * **Lưu ý:** Dữ liệu này sẽ tự làm sạch khi đóng trình duyệt hoặc F5.
            **ðŸ“Œ Ghi chÃº cho NgÆ° dÃ¢n:**
            * **GiÃ¡ lÆ°u:** má»©c giÃ¡ táº¡i thá»i Ä‘iá»ƒm Ä‘Æ°a cÃ¡ vÃ o táº§m ngáº¯m.
            * **Ká»· luáº­t:** Chá»‰ nÃªn giá»¯ tá»‘i Ä‘a 5-7 mÃ£ trong Sá»• VÃ ng Ä‘á»ƒ táº­p trung nguá»“n lá»±c.
            * **LÆ°u Ã½:** Dá»¯ liá»‡u nÃ y sáº½ tá»± lÃ m sáº¡ch khi Ä‘Ã³ng trÃ¬nh duyá»‡t hoáº·c F5.
            """
        )

        if st.button("🧹 Làm sạch sổ"):
        if st.button("ðŸ§¹ LÃ m sáº¡ch sá»•"):
            st.session_state.history_log = []
            st.rerun()
    else:
        st.info("Sổ vàng vẫn đang đợi những con cá lớn. Hãy nhấn nút 'Lưu vào Sổ Vàng' ở Tab Chi tiết để ghi lại mục tiêu.")
        st.info("Sá»• vÃ ng váº«n Ä‘ang Ä‘á»£i nhá»¯ng con cÃ¡ lá»›n. HÃ£y nháº¥n nÃºt 'LÆ°u vÃ o Sá»• VÃ ng' á»Ÿ Tab Chi tiáº¿t Ä‘á»ƒ ghi láº¡i má»¥c tiÃªu.")
