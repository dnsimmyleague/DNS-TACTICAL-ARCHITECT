import streamlit as st
from PIL import Image
from google import genai
from google.genai import types
import random

# ---------------------------------------------------------
# CẤU HÌNH GIAO DIỆN CHUNG - ẨN STREAMLIT - THEME HỆ KIM (VIP)
# ---------------------------------------------------------
st.set_page_config(page_title="DN SIM MY LEAGUE | VIP R&D", page_icon="👑", layout="wide")

custom_css = """
<style>
    /* 1. Xóa sạch dấu vết của Streamlit (Hàng Free) */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* 2. Màu nền Xám Than Không Gian (Charcoal) - Sang trọng */
    .stApp {
        background-color: #121418 !important; 
    }
    
    /* 3. Tiêu đề Kênh - Gradient Vàng Kim */
    .title-gradient {
        text-align: center;
        background: -webkit-linear-gradient(45deg, #D4AF37, #FFF8DC);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.5rem;
        font-weight: 900;
        margin-bottom: 10px;
        letter-spacing: 3px;
        text-shadow: 2px 2px 10px rgba(212, 175, 55, 0.3);
    }
    
    .slogan {
        text-align: center;
        color: #A9A9A9;
        font-size: 1.2rem;
        font-style: italic;
        margin-bottom: 40px;
        letter-spacing: 1px;
    }

    /* 4. Định dạng Nút Bấm Xử Lý Vàng Khối (Solid Gold) */
    .stButton > button { 
        width: 100%; 
        height: 65px; 
        font-size: 22px; 
        font-weight: 900; 
        text-transform: uppercase;
        background: linear-gradient(90deg, #D4AF37 0%, #B8860B 100%);
        color: #121418 !important; 
        border: none;
        border-radius: 8px;
        box-shadow: 0 4px 15px rgba(212, 175, 55, 0.4);
        transition: all 0.3s ease 0s;
    }
    .stButton > button:hover { 
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(212, 175, 55, 0.6);
        background: linear-gradient(90deg, #FFD700 0%, #D4AF37 100%);
    }

    /* 5. CẤU TRÚC PHIẾU VIP (ĐỂ SẾP CHỤP MÀN HÌNH GỬI KHÁCH) */
    .vip-card {
        background: linear-gradient(145deg, #1A1D24, #242933);
        border: 2px solid #D4AF37;
        border-radius: 15px;
        padding: 40px;
        margin-top: 20px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.8), 0 0 20px rgba(212, 175, 55, 0.2);
    }
    .vip-header {
        text-align: center;
        border-bottom: 2px solid #D4AF37;
        padding-bottom: 20px;
        margin-bottom: 30px;
    }
    .vip-logo { max-width: 150px; border-radius: 12px; margin-bottom: 15px; }
    .vip-brand { color: #D4AF37; font-size: 28px; font-weight: 900; letter-spacing: 2px; margin: 0; }
    .vip-text { color: #E0E0E0; font-family: 'Consolas', monospace; font-size: 16px; line-height: 1.6; white-space: pre-wrap; }
    .vip-footer {
        text-align: center;
        border-top: 2px solid #D4AF37;
        padding-top: 30px;
        margin-top: 40px;
    }
    .vip-qr { max-width: 150px; border-radius: 10px; border: 3px solid #D4AF37; margin-bottom: 10px;}
    .vip-copyright { color: #808080; font-size: 14px; margin-top: 10px;}
    
    /* Chỉnh khung copy text cho gọn gàng */
    .stTextArea textarea { 
        font-family: 'Consolas', monospace !important; 
        font-size: 14px !important; 
        background-color: #0d1117 !important; 
        color: #00ffcc !important; 
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)
st.markdown("<h1 class='title-gradient'>DN SIM MY LEAGUE</h1>", unsafe_allow_html=True)
st.markdown("<p class='slogan'>Giải Mã Sơ Đồ - Định Hình Meta - Kiến Tạo Dream Team</p>", unsafe_allow_html=True)

# ---------------------------------------------------------
# KHỐI NHẬP LIỆU (UI)
# ---------------------------------------------------------
col1, col2 = st.columns(2)
with col1:
    player_info = st.text_input("Tên Cầu thủ & Vị trí (Bỏ trống nếu muốn vẽ sơ đồ):", placeholder="Ví dụ: D. Bergkamp - CF")
    ecosystem = st.selectbox("Chọn hệ sinh thái (SIM AI / PvP):", ["SIM AI", "PvP"])
with col2:
    manager_name = st.text_input("Tên HLV (Bỏ trống nếu muốn khám bệnh cầu thủ):", placeholder="Ví dụ: R. Martínez (Quick Counter)...")
    uploaded_files = st.file_uploader("Tải ảnh Phôi thẻ hoặc HLV", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)

# ---------------------------------------------------------
# LÕI TRÍ TUỆ NHÂN TẠO (AI CORE)
# ---------------------------------------------------------
def execute_tactical_analysis(image_objs, p_info, eco, manager):
    try:
        api_key = st.secrets.get("GEMINI_API_KEY")
        if not api_key:
            return "[LỖI CẤU HÌNH]: Không tìm thấy GEMINI_API_KEY trong mục Advanced settings -> Secrets!"
            
        client = genai.Client(api_key=api_key)
        
        system_instruction = """
        Bạn là DNS TACTICAL ARCHITECT - Giám đốc Kỹ thuật kiêm Bậc thầy Chiến thuật eFootball. Phân tích của bạn là "Báo cáo nội bộ VIP" dành cho khách hàng trả phí.
        LỆNH TỐI THƯỢNG:
        1. VĂN BẢN SIÊU PHẲNG. TUYỆT ĐỐI KHÔNG dùng Markdown (*, #). Phân tách mục bằng ngoặc vuông [].
        2. Chuyên môn đỉnh cao: Giải thích rõ ý đồ chiến thuật, vẽ kịch bản Highlight, CHỈ TRÍCH AUTO OVR. CẤM đề xuất trùng skill có sẵn trong ảnh.
        3. TUYỆT ĐỐI KHÔNG BAO GIỜ SỬ DỤNG TỪ "(GIẤU)".
        
        KỊCH BẢN 1: KHI CHỈ CÓ HLV
        [PHÂN TÍCH TRIẾT LÝ HLV] Đánh giá Lối chơi.
        [SƠ ĐỒ TỐI ƯU] Đề xuất 1 sơ đồ.
        [QUY HOẠCH DREAM TEAM 23 NHÂN SỰ] Chi tiết 11 đá chính, 12 dự bị (Vị trí - Playstyle - Vai trò thực chiến). BẮT BUỘC liệt kê đủ 23 người. KHÔNG đề xuất tên cầu thủ cụ thể.
        [THIẾT LẬP LỆNH CÁ NHÂN] Chỉ định tấn công/phòng ngự.
        
        KỊCH BẢN 2: KHI CHỈ CÓ CẦU THỦ
        [ĐỌC VỊ TỐ CHẤT] Điểm mạnh/yếu chí mạng.
        [ĐỊNH HƯỚNG LỐI CHƠI] Hợp HLV nào.
        
        KỊCH BẢN 3: KHI CÓ CẢ CẦU THỦ VÀ HLV (ÉP CHỈ SỐ DÀNH CHO CONTENT)
        [VAI TRÒ THỰC CHIẾN] Cầu thủ đá vai trò gì trong sơ đồ HLV này?
        [TỔNG QUỸ PP] Quét Points X/Y. Lấy Y làm tổng.
        [CÔNG THỨC MANUAL BUILD ĐỘC QUYỀN] Chỉ số cụ thể kèm 1 câu giải thích ý đồ phân bổ (Ví dụ: Bỏ qua phòng thủ, dồn sức vào tăng tốc).
        [BOOSTER & TOP 5 SKILL] Đề xuất 1 Booster (nếu thỏa điều kiện) + 5 Skill mới KHÔNG TRÙNG SKILL TRONG ẢNH. BẮT BUỘC giải thích vai trò từng skill.
        [BÓC TÁCH AUTO VS MANUAL] Tại sao Auto OVR lại ngu ngốc/lãng phí với con hàng này? Manual buff thêm vào đâu để tối ưu? (Phục vụ làm kịch bản Video so sánh).
        [KỊCH BẢN HIGHLIGHT IN-GAME] Tưởng tượng 2 tình huống ghi bàn/kiến tạo/phòng ngự điển hình trong game thực tế dựa trên thông số Manual Build này.
        """
        config = types.GenerateContentConfig(system_instruction=system_instruction, temperature=0.3)
        
        has_p = bool(p_info.strip())
        has_m = bool(manager.strip())
        
        if has_m and not has_p: kich_ban = "KỊCH BẢN 1: TƯ DUY KIẾN TRÚC SƯ"
        elif has_p and not has_m: kich_ban = "KỊCH BẢN 2: TUYỂN TRẠCH VIÊN"
        else: kich_ban = "KỊCH BẢN 3: R&D ÉP CHỈ SỐ - CONTENT TRIỆU VIEW"
            
        p_stat = p_info if has_p else "KHÔNG CÓ"
        m_stat = manager if has_m else "KHÔNG CÓ"
        context_prompt = f"Cầu thủ: {p_stat} | HLV: {m_stat} | Chế độ: {eco}. THỰC THI DUY NHẤT: {kich_ban}."
        
        contents = [context_prompt]
        if image_objs: contents.extend(image_objs)
            
        response = client.models.generate_content(model='gemini-3.6-flash', contents=contents, config=config)
        return response.text
    except Exception as e:
        return f"[LỖI HỆ THỐNG AI]: {str(e)}"

# ---------------------------------------------------------
# XỬ LÝ SỰ KIỆN VÀ IN PHIẾU VIP BẰNG HTML
# ---------------------------------------------------------
if st.button("[BẮT ĐẦU PHÂN TÍCH VIP]"):
    if 'analysis_report' in st.session_state: del st.session_state['analysis_report']
        
    if not uploaded_files: st.error("Thiếu dữ liệu: Vui lòng tải ảnh Phôi thẻ/HLV lên!")
    elif not player_info and not manager_name: st.error("Thiếu dữ liệu: Nhập tên Cầu thủ hoặc HLV!")
    else:
        with st.spinner("Đang truy xuất CSDL và trích xuất Báo cáo VIP..."):
            images = [Image.open(f) for f in uploaded_files]
            st.session_state['analysis_report'] = execute_tactical_analysis(images, player_info, ecosystem, manager_name)
            st.session_state['text_key'] = str(random.randint(1000, 9999))

# --- KHU VỰC IN PHIẾU VIP ĐỂ SẾP CHỤP MÀN HÌNH ---
if 'analysis_report' in st.session_state:
    
    # Đã cập nhật 2 link ảnh sống nhăn răng của sếp
    LINK_LOGO = "https://i.postimg.cc/f3TrLpQc/044111AB-7F8B-4DBE-B375-A9EBF547FE57.jpg"
    LINK_QR = "https://i.postimg.cc/4KNSdqRd/D9754823-56B4-4957-8F90-1EE072CFF5A2.jpg"
    
    vip_html = f"""
<div class="vip-card">
<div class="vip-header">
<img src="{LINK_LOGO}" class="vip-logo">
<h2 class="vip-brand">DN SIM MY LEAGUE</h2>
<p style="color: #A9A9A9; font-style: italic; margin-top: -10px;">Báo cáo Kỹ thuật Độc quyền (VIP)</p>
</div>
<div class="vip-text">
{st.session_state['analysis_report']}
</div>
<div class="vip-footer">
<h3 style="color: #D4AF37; margin-bottom: 15px;">ỦNG HỘ DN SIM MY LEAGUE</h3>
<img src="{LINK_QR}" class="vip-qr">
<p class="vip-copyright">© 2026 Bản quyền phân tích thuộc về DN SIM MY LEAGUE. Cấm sao chép dưới mọi hình thức.</p>
</div>
</div>
"""
    st.markdown(vip_html, unsafe_allow_html=True)
    
    if 'text_key' not in st.session_state:
        st.session_state['text_key'] = "default_key"
        
    with st.expander("Bấm vào đây để Copy văn bản thô (Dành cho Team Content lên Kịch bản Video)"):
        st.text_area("Văn bản gốc:", value=st.session_state['analysis_report'], height=200, key=f"text_area_{st.session_state['text_key']}")
