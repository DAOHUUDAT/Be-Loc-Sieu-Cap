import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

@st.cache_data # Dùng cache để app chỉ tải một lần, cực nhanh
def load_vietstock_data():
    urls = [
        "https://github.com/DAOHUUDAT/Be-Loc-Sieu-Cap/raw/refs/heads/main/data/HOSE.xlsx",
        "https://github.com/DAOHUUDAT/Be-Loc-Sieu-Cap/raw/refs/heads/main/data/HNX.xlsx",
        "https://github.com/DAOHUUDAT/Be-Loc-Sieu-Cap/raw/refs/heads/main/data/UPCOM.xlsx"
    ]
    # Gộp 3 sàn thành 1 đại dương dữ liệu duy nhất
    combined_df = pd.concat([pd.read_excel(url) for url in urls])
    return combined_df

# Kích hoạt dữ liệu nền
vietstock_db = load_vietstock_data()

def get_star_rating(g_margin, debt_ratio, ttm_profit):
    stars = 0
    # Tiêu chí 1: Biên lợi nhuận gộp tốt (>15%)
    if g_margin > 15: stars += 2
    elif g_margin > 10: stars += 1
    
    # Tiêu chí 2: Tài chính lành mạnh (Nợ/CSH < 1.0)
    if debt_ratio < 1.0: stars += 2
    elif debt_ratio < 1.5: stars += 1
    
    # Tiêu chí 3: Có lãi TTM
    if ttm_profit > 0: stars += 1
    
    return "⭐" * stars if stars > 0 else "🥚 (Cần theo dõi thêm)"

# --- 1. CẤU HÌNH HỆ THỐNG GIAO DIỆN ---
st.set_page_config(page_title="HÃY CHỌN CÁ ĐÚNG v6.3.5", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 1.6rem !important; font-weight: bold; color: #007bff; }
    section[data-testid="stSidebar"] { width: 310px !important; }
    .stTable { border-radius: 12px; overflow: hidden; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { border-radius: 5px; padding: 10px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

if 'history_log' not in st.session_state: 
    st.session_state['history_log'] = []

# --- HÀM TÍNH TOÁN KỸ THUẬT (Các tấm lọc) ---
# --- TỪ ĐIỂN VIỆT HÓA BCTC SIÊU CẤP ---
DICTIONARY_BCTC = {
    # Doanh thu & Lợi nhuận gộp
    'Total Revenue': 'Tổng Doanh thu',
    'Operating Revenue': 'Doanh thu hoạt động',
    'Cost Of Revenue': 'Giá vốn hàng bán',
    'Gross Profit': 'Lợi nhuận gộp',
    
    # Chi phí hoạt động
    'Operating Expense': 'Chi phí hoạt động',
    'Selling General And Administration': 'Chi phí bán hàng & QLDN',
    'Selling And Marketing Expense': 'Chi phí bán hàng & Marketing',
    'General And Administrative Expense': 'Chi phí quản lý doanh nghiệp',
    'Rent Expense Supplemental': 'Chi phí thuê bổ sung',
    'Rent And Landing Fees': 'Chi phí thuê & phí bãi',
    'Depreciation And Amortization In Income Statement': 'Khấu hao trong BCKQKD',
    'Depreciation Income Statement': 'Khấu hao (BCKQKD)',
    
    # Lợi nhuận hoạt động & Khác
    'Operating Income': 'Lợi nhuận từ HĐKD',
    'Total Operating Income As Reported': 'Tổng LN hoạt động (Báo cáo)',
    'Total Expenses': 'Tổng chi phí',
    'Other Non Operating Income Expenses': 'Thu nhập/Chi phí phi hoạt động khác',
    'Special Income Charges': 'Chi phí thu nhập đặc biệt',
    'Other Special Charges': 'Chi phí đặc biệt khác',
    
    # Tài chính & Lãi vay
    'Net Interest Income': 'Thu nhập lãi thuần',
    'Interest Income': 'Thu nhập lãi vay',
    'Interest Expense': 'Chi phí lãi vay',
    'Interest Income Non Operating': 'Thu nhập lãi phi hoạt động',
    'Interest Expense Non Operating': 'Chi phí lãi phi hoạt động',
    'Net Non Operating Interest Income Expense': 'Thu nhập lãi phi hoạt động thuần',
    'Total Other Finance Cost': 'Tổng chi phí tài chính khác',
    
    # Lợi nhuận trước & sau thuế
    'Pretax Income': 'Lợi nhuận trước thuế',
    'Tax Provision': 'Dự phòng thuế',
    'Tax Rate For Calcs': 'Thuế suất tính toán',
    'Net Income Continuous Operations': 'LN từ HĐ liên tục',
    'Net Income Including Noncontrolling Interests': 'LN ròng gồm lợi ích CĐTS',
    'Minority Interests': 'Lợi ích cổ đông thiểu số',
    'Net Income': 'Lợi nhuận ròng',
    'Net Income Common Stockholders': 'LN ròng dành cho CĐ phổ thông',
    'Net Income From Continuing Operation Net Minority Interest': 'LN ròng từ HĐKD liên tục (sau CĐTS)',
    'Net Income From Continuing And Discontinued Operation': 'LN từ HĐ liên tục & gián đoạn',
    'Normalized Income': 'Lợi nhuận điều chỉnh (Normalized)',
    
    # EPS & Cổ phiếu
    'Basic EPS': 'EPS cơ bản',
    'Diluted EPS': 'EPS pha loãng',
    'Basic Average Shares': 'Số CP lưu hành bình quân',
    'Diluted Average Shares': 'Số CP pha loãng bình quân',
    'Otherunder Preferred Stock Dividend': 'Cổ tức CP ưu đãi khác',
    
    # EBITDA & Chỉ số tính toán
    'EBITDA': 'EBITDA',
    'EBIT': 'EBIT',
    'Normalized EBITDA': 'EBITDA điều chỉnh',
    'Reconciled Depreciation': 'Khấu hao đã đối soát',
    'Reconciled Cost Of Revenue': 'Giá vốn đã đối soát',
    'Total Unusual Items': 'Tổng các khoản bất thường',
    'Total Unusual Items Excluding Goodwill': 'Tổng khoản bất thường (ko gồm Lợi thế TM)',
    'Tax Effect Of Unusual Items': 'Ảnh hưởng thuế của khoản bất thường'
}
def compute_rsi(data, window=14):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# --- 2. SIDEBAR: TRI KỶ & CẨM NANG CHIẾN THUẬT ---
with st.sidebar:
    # 1. Ảnh Tri Kỷ
    img_url = "https://github.com/DAOHUUDAT/Be-Loc-Sieu-Cap/blob/main/anh-tri-ky.jpg?raw=true"
    st.markdown(
        f"""
        <div style="display: flex; justify-content: center;">
            <img src="{img_url}" style="width: 100%; border-radius: 15px; border: 2px solid #007bff; margin-bottom: 20px;" 
                 onerror="this.onerror=null; this.src='https://cdn-icons-png.flaticon.com/512/1144/1144760.png';">
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.header("🎮 ĐÀI CHỈ HUY")
    t_input = st.text_input("🔍 SOI MÃ CÁ", "VNI").upper()
    st.divider()

    # 2. Cẩm Nang Toàn Diện (Đã sửa lỗi thụt lề)
    st.header("📓 CẨM NANG")
    with st.expander("📖 Giải mã thông số", expanded=True):
        # PHẦN TỔNG QUÁT (Hệ tư tưởng Trường Money)
        st.markdown("### 🚀 Hệ sinh thái Cá:")
        st.write("- **SIÊU CÁ:**ội tụ 3 yếu tố: Giá > MA20 + Vol đột biến (>120%) + Sức mạnh RS khỏe hơn VN-Index.")
        st.write("- **Cá Lớn 🐋:** Xu hướng tăng bền vững (Giá nằm trên cả MA20 và MA50).")
        st.write("- **Cá Đang Lớn 🐡:** Giai đoạn chuyển mình, vừa chớm vượt MA20.")
        st.write("- **Cá Nhỏ 🐟:** Dưới trung bình, dòng tiền yếu - Tạm bỏ qua.")

        st.markdown("### 🌡️ Trạng thái dòng nước:")
        st.write("- **💪 Khỏe:** Sức mạnh tương đối (RS) dương - cá đang bơi khỏe hơn thị trường chung.")
        st.write("- **🌊 Sóng:** Vol > 150% trung bình 20 phiên - dấu hiệu 'cá mập' đang đẩy giá.")
        st.write("- **🌡️ Nhiệt độ (RSI):** Nóng (>70) dễ điều chỉnh, Lạnh (<30) quá bán.")
        
        st.divider() 
        
        # PHẦN CHI TIẾT (Lý giải chuyên sâu cho Tab Phân Tích)
        st.markdown(f"### 💎 Mổ xẻ chi tiết: {t_input}")
        st.write("- **🛡️ Niềm tin (%):** Chỉ số đo lường sự đồng thuận giữa Tăng trưởng doanh thu và Vị thế giá kỹ thuật. >80% là Siêu Cá hội tụ đủ Thiên thời & Địa lợi.")
        st.write("- **💰 Định giá 3 kịch bản:**")
        st.write("    * *Thận trọng:* Vùng giá mua an toàn nhất (Margin of Safety), đã trừ hao rủi ro.")
        st.write("    * *Cơ sở:* Giá trị hợp lý của cá trong điều kiện tăng trưởng bình thường.")
        st.write("    * *Phi thường:* Mục tiêu khi cá bước vào siêu sóng tăng trưởng đột biến.")
        st.write("- **📈 Tuyệt kỹ Ichimoku:**")
        st.write("    * *Mây (Kumo):* Vùng hỗ trợ/kháng cự tâm lý. Giá trên mây xanh là vùng trời tăng trưởng tự do.")
        st.write("    * *Tím (Tenkan):* Tín hiệu tốc độ ngắn hạn (9 phiên). Tenkan cắt lên Kijun là điểm cá quẫy đuôi tăng tốc.")
        st.write("    * *Vàng (Kijun):* Đường xương sống bền vững (26 phiên). Cá còn nằm trên Kijun là xu hướng tăng còn giữ vững.")
        
        # --- ĐÂY LÀ PHẦN BỔ SUNG MỚI ---
        st.write("- **🍱 Chiến thuật 'Thức ăn':**")
        st.write("    * *Định nghĩa:* Là khoảng cách (dư địa) giữa giá hiện tại và đường trung bình MA20.")
        st.write("    * *Lý giải:* Theo quy luật hồi mã, giá thường có xu hướng quay lại MA20 như con cá quay về nơi có thức ăn. Nếu % âm lớn, cá đang 'đói' (quá xa hỗ trợ) -> rủi ro điều chỉnh cao. Nếu % dương nhỏ, cá đang ở vùng 'no nê' (gần hỗ trợ) -> an toàn để thả lưới.")
        # ------------------------------

        st.write("- **🍱 Chiến thuật:** Kiểm tra 'Thức ăn' (% dư địa về MA20)...") # Dòng cũ của bạn
    # 3. Kim Chỉ Nam (Quotes)
    st.divider()
    QUOTES = [
        "“Trong đầu tư, thứ đắt đỏ nhất là sự thiếu kiên nhẫn.”",
        "“Hãy mua con cá khỏe nhất trong dòng nước yếu nhất.”",
        "“Đừng cố bắt cá khi đại dương đang có bão lớn.”",
        "“Siêu cá không xuất hiện mỗi ngày, hãy kiên nhẫn đợi điểm nổ.”",
        "“Kỷ luật là thứ tách biệt ngư dân chuyên nghiệp và kẻ đi dạo.”",
        "“Giá là thứ bạn trả, giá trị là thứ con cá mang lại.”"
    ]
    import random
    st.info(f"💡 {random.choice(QUOTES)}")

    # --- 2.4 TUYÊN BỐ MIỄN TRỪ TRÁCH NHIỆM ---
    st.divider()
    st.caption("""
    ⚠️ **MIỄN TRỪ TRÁCH NHIỆM:** Mọi dữ liệu và phân tích từ 'Bể Lọc' chỉ mang tính chất tham khảo, hỗ trợ ra quyết định. 
    Đầu tư tài chính luôn tiềm ẩn rủi ro. Chúng tôi không chịu trách nhiệm cho bất kỳ 
    tổn thất nào phát sinh từ việc sử dụng các thông tin này. 
    Hãy luôn tự tìm hiểu và quản trị rủi ro cá nhân.
    """)

st.title("🚀 Bể Lọc v6.3.15: HÃY CHỌN CÁ ĐÚNG")

# --- 3. TRẠM QUAN TRẮC ĐẠI DƯƠNG (VN-INDEX) ---
inf_factor = 1.0 
try:
    vni = yf.download("^VNI", period="150d", progress=False)
    if not vni.empty:
        if isinstance(vni.columns, pd.MultiIndex): vni.columns = vni.columns.get_level_values(0)
        v_c = float(vni['Close'].iloc[-1])
        vh26 = vni['High'].rolling(26).max(); vl26 = vni['Low'].rolling(26).min()
        vh9 = vni['High'].rolling(9).max(); vl9 = vni['Low'].rolling(9).min()
        vsa = (((vh9+vl9)/2 + (vh26+vl26)/2)/2).shift(26).iloc[-1]
        
        # Hệ số an toàn co giãn (Triết lý bản v5.5)
        inf_factor = 1.15 if v_c > vsa else 0.85
        st.info(f"🌊 Đại Dương: {'🟢 THẢ LƯỚI (Sóng Thuận)' if v_c > vsa else '🔴 ĐÁNH KẺNG (Sóng Nghịch)'} | Co giãn: {inf_factor}x")
except: pass

# --- 4. HỆ THỐNG TABS ---
# Thay dòng st.tabs cũ bằng dòng này để lưu trạng thái vào biến selected_tab
tab_radar, tab_analysis, tab_bctc, tab_history = st.tabs(["🎯 RADAR ELITE", "💎 CHI TIẾT SIÊU CÁ", "📊 MỔ XẺ BCTC", "📓 SỔ VÀNG"])

with tab_radar:
    st.subheader("🤖 Top 20 SIÊU CÁ")
    
    # Hiển thị trạng thái Đại dương để làm tham chiếu
    status_color = "green" if inf_factor > 1 else "red"
    st.markdown(f"**Trạng thái dòng nước:** <span style='color:{status_color}'>{ '🌊 Thuận lợi (Hệ số x' + str(inf_factor) + ')' if inf_factor > 1 else '⚠️ Khó khăn (Hệ số x' + str(inf_factor) + ')' }</span>", unsafe_allow_html=True)
    
    # Danh mục 20 mã trọng điểm
    elite_20 = ["DGC", "MWG", "FPT", "TCB", "SSI", "HPG", "GVR", "CTR", "DBC", "VNM", "STB", "MBB", "ACB", "KBC", "VGC", "PVS", "PVD", "ANV", "VHC", "REE"]
    radar_list = []
    
    with st.spinner('Đang tầm soát siêu cá...'):
        for tk in elite_20:
            try:
                # Tải dữ liệu 100 phiên để tính toán MA50 và RS
                d = yf.download(f"{tk}.VN", period="100d", progress=False)
                if not d.empty:
                    if isinstance(d.columns, pd.MultiIndex): d.columns = d.columns.get_level_values(0)
                    
                    p_c = d['Close'].iloc[-1]
                    v_now = d['Volume'].iloc[-1]
                    v_avg = d['Volume'].rolling(20).mean().iloc[-1]
                    ma20 = d['Close'].rolling(20).mean().iloc[-1]
                    ma50 = d['Close'].rolling(50).mean().iloc[-1]
                    
                    # 1. Tính nhiệt độ RSI
                    d['rsi_val'] = compute_rsi(d['Close'])
                    curr_rsi = d['rsi_val'].iloc[-1]
                    temp = "🔥 Nóng" if curr_rsi > 70 else "❄️ Lạnh" if curr_rsi < 30 else "🌤️ Êm"
                    
                    # 2. Tính sức mạnh tương quan (RS - Relative Strength)
                    # Hiệu suất mã vs VN-Index trong 20 phiên
                    stock_perf = (p_c / d['Close'].iloc[-20]) - 1
                    vni_perf = (v_c / vni['Close'].iloc[-20]) - 1 if not vni.empty else 0
                    is_stronger = stock_perf > vni_perf
                    
                    # 3. PHÂN LOẠI SIÊU CÁ (Theo triết lý hôm qua đã nghiên cứu)
                    # Điều kiện Siêu Cá: Giá > MA20, Vol > 1.2x trung bình, và Khỏe hơn Đại dương
                    if p_c > ma20 and v_now > v_avg * 1.2 and is_stronger:
                        loai_ca = "🚀 SIÊU CÁ"
                        priority = 1
                    elif p_c > ma20 and p_c > ma50:
                        loai_ca = "Cá Lớn 🐋"
                        priority = 2
                    elif p_c > ma20:
                        loai_ca = "Cá Đang Lớn 🐡"
                        priority = 3
                    else:
                        loai_ca = "Cá Nhỏ 🐟"
                        priority = 4
                        
                    radar_list.append({
                        "Mã": tk, 
                        "Giá": f"{p_c:,.0f}",
                        "Sóng": "🌊 Mạnh" if v_now > v_avg * 1.5 else "☕ Lặng",
                        "Nhiệt độ": temp,
                        "Đại Dương": "💪 Khỏe" if is_stronger else "🐌 Yếu",
                        "Loại": loai_ca,
                        "Thức ăn": f"{((ma20/p_c)-1)*100:+.1f}%" if p_c < ma20 else "✅ Đang no",
                        "priority": priority
                    })
            except: continue
            
    # Sắp xếp để Siêu Cá hiện lên đầu danh sách
    df_radar = pd.DataFrame(radar_list).sort_values(by="priority")

    # --- ĐOẠN FIX: BIẾN BẢNG THÀNH BỘ CẢM BIẾN ---
    df_radar = pd.DataFrame(radar_list).sort_values(by="priority")
    
    # Sử dụng st.dataframe để kích hoạt tính năng chọn dòng
    selection = st.dataframe(
        df_radar.drop(columns=['priority']),
        use_container_width=True,
        hide_index=True,
        selection_mode="single_row", # Cho phép chọn 1 mã
        on_select="rerun"            # Click là app tự nạp lại dữ liệu
    )

    # Nếu bro click vào một dòng, lưu mã đó vào bộ nhớ 'selected_ticker'
    if len(selection.selection.rows) > 0:
        selected_index = selection.selection.rows[0]
        ticker_clicked = df_radar.iloc[selected_index]['Mã']
        st.session_state.selected_ticker = ticker_clicked
        # Ép app ghi nhận mã mới ngay lập tức
        st.rerun()

with tab_analysis:
    # --- ĐOẠN FIX: TỰ ĐỘNG ĐIỀN MÃ KHI CLICK ---
    # Kiểm tra xem có mã nào được chọn từ Radar chưa, nếu chưa mặc định là HSG
    init_ticker = st.session_state.get('selected_ticker', "HSG")
    
    t_input = st.text_input(
        "Nhập mã cá muốn mổ xẻ:", 
        value=init_ticker,
        key="main_search_input" # Thêm key để tránh xung đột dữ liệu
    ).upper()
    # ---------------------------------------------------
    try:
        t_obj = yf.Ticker(f"{t_input}.VN")
        s_df = t_obj.history(period="1y")
        if isinstance(s_df.columns, pd.MultiIndex): s_df.columns = s_df.columns.get_level_values(0)
        curr_p = float(s_df['Close'].iloc[-1])
        
        # Lấy dữ liệu tài chính cho biểu đồ 5 quý
        fin_q = t_obj.quarterly_financials
        
        # TÍNH NIỀM TIN (Đã fix lỗi thiếu dữ liệu)
        try:
            # Kiểm tra xem có đủ ít nhất 5 quý không
            if len(fin_q.columns) >= 5:
                rev_growth = ((fin_q.loc['Total Revenue'].iloc[0] / fin_q.loc['Total Revenue'].iloc[4]) - 1)
            else:
                # Nếu thiếu dữ liệu, tính dựa trên số quý hiện có
                rev_growth = ((fin_q.loc['Total Revenue'].iloc[0] / fin_q.loc['Total Revenue'].iloc[-1]) - 1)
            
            # Tính điểm trust
            trust = int(min(100, (rev_growth * 100) + (50 if curr_p > s_df['Close'].rolling(50).mean().iloc[-1] else 0)))
        except Exception as e: 
            rev_growth = 0.1
            trust = 65

        # 1. Hiển thị Chỉ số & Định giá
        st.markdown(f"### 🛡️ Niềm tin {t_input}: {trust}%")
        c_p, c1, c2, c3 = st.columns(4)
        p_base = curr_p * (1 + rev_growth) * inf_factor
        c_p.metric("📍 GIÁ HIỆN TẠI", f"{curr_p:,.0f}")
        c1.metric("🐢 Thận trọng", f"{curr_p * (1 + rev_growth * 0.4) * inf_factor:,.0f}")
        c2.metric("🏠 Cơ sở", f"{p_base:,.0f}")
        c3.metric("🚀 Phi thường", f"{curr_p * (1 + rev_growth * 2) * inf_factor:,.0f}")

        # --- PHẦN ĐÃ TINH CHỈNH: BIỂU ĐỒ TÀI CHÍNH 5 QUÝ CÓ SỐ LIỆU ---
        st.subheader("📊 Sức khỏe tài chính 5 Quý gần nhất (Tỷ VNĐ)")
        if not fin_q.empty:
            # Lấy Doanh thu và Lợi nhuận ròng, chia cho 1 tỷ để đổi đơn vị
            q_rev = (fin_q.loc['Total Revenue'].iloc[:5][::-1]) / 1e9 
            try:
                q_net = (fin_q.loc['Net Income'].iloc[:5][::-1]) / 1e9
            except:
                q_net = (fin_q.loc['Net Income From Continuing Operation Net Extraordinaries'].iloc[:5][::-1]) / 1e9
            
            fig_fin = go.Figure()
            
            # Thêm cột Doanh thu với số liệu hiển thị
            fig_fin.add_trace(go.Bar(
                x=q_rev.index.astype(str), 
                y=q_rev, 
                name='Doanh thu', 
                marker_color='#007bff',
                text=q_rev.apply(lambda x: f"{x:,.0f}"), # Hiển thị số nguyên tỷ VNĐ
                textposition='auto'
            ))
            
            # Thêm cột Lợi nhuận với số liệu hiển thị
            fig_fin.add_trace(go.Bar(
                x=q_net.index.astype(str), 
                y=q_net, 
                name='Lợi nhuận', 
                marker_color='#FFD700',
                text=q_net.apply(lambda x: f"{x:,.1f}"), # Hiển thị 1 chữ số thập phân cho lợi nhuận
                textposition='auto'
            ))
            
            fig_fin.update_layout(
                barmode='group', 
                height=350, 
                margin=dict(l=0,r=0,t=30,b=0), 
                template="plotly_white",
                yaxis_title="Tỷ VNĐ"
            )
            st.plotly_chart(fig_fin, use_container_width=True)

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

with tab_bctc:
    st.subheader(f"📊 Mổ xẻ nội tạng Cá: {t_input}")
    
    # 1. Khu vực tải PDF (Giữ nguyên cho Gemini mổ xẻ sau)
    uploaded_file = st.file_uploader(f"📂 Tải lên BCTC PDF của {t_input}", type=['pdf'])
    if uploaded_file:
        st.success(f"✅ Đã nhận file. Gemini sẵn sàng mổ xẻ mã {t_input}!")

    st.divider()

    if t_input and not vietstock_db.empty:
        # TRUY VẤN DỮ LIỆU TỪ FILE EXCEL VIETSTOCK
        fish_data = vietstock_db[vietstock_db['Mã CK'] == t_input]
        
        if not fish_data.empty:
            row = fish_data.iloc[0]
            
            # --- TỰ ĐỘNG TÌM CỘT DỰA TRÊN TỪ KHÓA (Vì tiêu đề Vietstock rất dài) ---
            # Ví dụ: "Tổng doanh thu bán hàng...", "Lợi nhuận sau thuế...", "Hàng tồn kho..."
            def find_col(keyword):
                cols = [c for c in vietstock_db.columns if keyword.lower() in str(c).lower()]
                return cols[0] if cols else None

            col_rev = find_col("Doanh thu thuần") or find_col("Doanh thu bán hàng")
            col_profit = find_col("Lợi nhuận sau thuế")
            col_inventory = find_col("Hàng tồn kho")
            col_cash = find_col("Tiền và các khoản tương đương tiền")

            # --- GIAO DIỆN HIỂN THỊ 2 CỘT ---
            col_fa1, col_fa2 = st.columns([2, 1])
            
            with col_fa1:
                st.write("**📑 Thông số tài chính cốt lõi (Từ file Excel):**")
                # Hiển thị bảng tóm tắt các chỉ số quan trọng tìm được
                summary_data = {
                    "Chỉ số": ["Doanh thu", "Lợi nhuận sau thuế", "Hàng tồn kho", "Tiền mặt"],
                    "Giá trị (VND)": [
                        f"{row[col_rev]:,.0f}" if col_rev else "N/A",
                        f"{row[col_profit]:,.0f}" if col_profit else "N/A",
                        f"{row[col_inventory]:,.0f}" if col_inventory else "N/A",
                        f"{row[col_cash]:,.0f}" if col_cash else "N/A"
                    ]
                }
                st.table(pd.DataFrame(summary_data))
                
            with col_fa2:
                st.write("**🏆 Đánh giá nhanh:**")
                if col_profit and col_rev:
                    val_profit = row[col_profit]
                    val_rev = row[col_rev]
                    
                    st.metric("Lợi nhuận", f"{val_profit/1e9:,.2f} Tỷ")
                    
                    # Tính Biên lợi nhuận ròng tạm tính
                    net_margin = (val_profit / val_rev) * 100 if val_rev > 0 else 0
                    st.metric("Biên Lợi Nhuận Ròng", f"{net_margin:.1f}%")

                    if val_profit > 0:
                        st.success("🌟 Cá có lãi, nội tạng tốt!")
                    else:
                        st.error("⚠️ Cá đang sụt cân (Lỗ)")

            st.divider()
            
            # --- TƯ DUY A7 & TRƯỜNG MONEY ---
            st.subheader("🧠 Phân tích chuyên sâu (Tầm nhìn A7)")
            c1, c2 = st.columns(2)
            with c1:
                if col_inventory:
                    st.info(f"📦 **Của để dành (Tồn kho):** {row[col_inventory]/1e9:,.1f} Tỷ")
            with c2:
                if col_cash:
                    st.info(f"💰 **Sức mạnh tiền mặt:** {row[col_cash]/1e9:,.1f} Tỷ")

            st.info(f"💡 **Lời khuyên:** Kiểm tra xem 'Hàng tồn kho' có phải là các dự án sắp mở bán không. Đó là ngòi nổ cho SIÊU CÁ!")

        else:
            st.warning(f"Mã {t_input} không có trong bộ dữ liệu 3 sàn. Bro hãy kiểm tra lại file Excel.")
    else:
        st.info("Bro hãy chọn một con cá ở Tab Radar hoặc nhập mã để bắt đầu mổ xẻ.")

with tab_history:
    st.subheader("📓 DANH SÁCH CÁ ĐÃ TẦM SOÁT")
    if st.session_state.history_log:
        # Hiển thị bảng danh sách
        st.table(pd.DataFrame(st.session_state.history_log))
        
        # --- PHẦN GHI CHÚ BỔ SUNG ---
        st.info("""
        **📌 Ghi chú cho Ngư dân:**
        * **Giá lưu:** Là mức giá tại thời điểm bro quyết định đưa cá vào tầm ngắm. Hãy so sánh với giá hiện tại để thấy hiệu quả.
        * **Kỷ luật:** Chỉ nên giữ tối đa 5-7 mã trong Sổ Vàng để tập trung nguồn lực.
        * **Lưu ý:** Dữ liệu này sẽ tự làm sạch khi bro đóng trình duyệt hoặc F5. Hãy ghi lại ra sổ tay nếu đó là 'Siêu cá' dài hạn.
        """)
        
        if st.button("🗑️ Làm sạch sổ"):
            st.session_state.history_log = []
            st.rerun()
    else: 
        st.info("Sổ vàng vẫn đang đợi những con cá lớn. Hãy nhấn nút 'Lưu vào Sổ Vàng' ở Tab Chi tiết để ghi lại mục tiêu.")