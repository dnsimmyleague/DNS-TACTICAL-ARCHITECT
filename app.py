import streamlit as st
from PIL import Image
from google import genai
from google.genai import types
import random
import gc
import re

# ---------------------------------------------------------
# 1. CẤU HÌNH GIAO DIỆN MỆNH KIM PREMIUM (TƯƠI SÁNG, SANG TRỌNG)
# ---------------------------------------------------------
st.set_page_config(page_title="DN SIM MY LEAGUE | VIP DNS", page_icon="👑", layout="centered")

custom_css = """
<style>
    /* Xóa thanh trang trí của Streamlit */
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    
    /* Khóa màu nền Titanium Slate tươi sáng, không bị tối u ám */
    .stApp {
        background-color: #1E222A !important;
    }
    
    /* Tiêu đề Vàng Hoàng Kim Mệnh Kim */
    .title-brand { 
        text-align: center; 
        color: #FFD700 !important; 
        font-size: 2.4rem; 
        font-weight: 900; 
        margin-bottom: 5px; 
        letter-spacing: 2px;
        text-shadow: 0px 2px 10px rgba(255, 215, 0, 0.3);
    }
    
    .slogan { 
        text-align: center; 
        color: #E0E6ED !important; 
        font-size: 1.05rem; 
        font-style: italic; 
        margin-bottom: 25px; 
    }

    /* Khung nhập liệu sáng rõ, dễ đọc */
    .stTextInput > div > div > input, .stSelectbox > div > div > div {
        background-color: #F4F6F9 !important;
        color: #111827 !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        border: 1px solid #D4AF37 !important;
    }
    
    label {
        color: #FFD700 !important;
        font-weight: bold !important;
    }

    /* Nút bấm Vàng Hoàng Kim rực rỡ */
    .stButton > button { 
        width: 100%; 
        height: 55px; 
        font-size: 19px; 
        font-weight: 900; 
        background: linear-gradient(135deg, #FFD700 0%, #D4AF37 100%) !important; 
        color: #121418 !important; 
        border: none !important; 
        border-radius: 8px !important;
        box-shadow: 0 4px 12px rgba(212, 175, 55, 0.4);
    }

    /* Tab 3D nổi khối Bạch Kim & Gold */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { 
        background-color: #2A2F3A !important;
        border: 1px solid #D4AF37 !important;
        border-bottom: none !important;
        border-radius: 8px 8px 0px 0px !important;
        padding: 10px 16px !important; 
        color: #E0E6ED !important;
    }
    
    .stTabs [aria-selected="true"] { 
        background-color: #FFD700 !important; 
        color: #121418 !important; 
        font-weight: 900 !important;
        transform: translateY(-3px);
        box-shadow: 0 -4px 10px rgba(255, 215, 0, 0.3);
    }
    
    /* Khung Báo Cáo VIP */
    .vip-card { 
        background-color: #252A34 !important; 
        border: 2px solid #FFD700 !important; 
        border-radius: 0px 10px 10px 10px; 
        padding: 22px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.3);
    }
    
    .vip-text { 
        font-family: 'Consolas', monospace; 
        font-size: 14.5px; 
        line-height: 1.6; 
        white-space: pre-wrap; 
        color: #F3F4F6 !important; 
    }
    
    .vip-footer { 
        text-align: center; 
        border-top: 1px dashed #FFD700; 
        padding-top: 15px; 
        margin-top: 20px; 
        color: #9CA3AF; 
        font-size: 12px; 
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# Đầu trang Thương hiệu
st.markdown("<h1 class='title-brand'>DN SIM MY LEAGUE</h1>", unsafe_allow_html=True)
st.markdown("<p class='slogan'>Giải Mã Sơ Đồ - Định Hình Meta - Kiến Tạo Dream Team</p>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. KHỐI NHẬP LIỆU
# ---------------------------------------------------------
player_info = st.text_input("Tên Cầu thủ & Vị trí (Bỏ trống nếu vẽ sơ đồ):", placeholder="Ví dụ: D. Bergkamp - CF")
ecosystem = st.selectbox("Chọn hệ sinh thái (PvP / SIM AI):", ["PvP", "SIM AI"])
manager_name = st.text_input("Tên HLV (Bỏ trống nếu khám bệnh cầu thủ):", placeholder="Ví dụ: R. Martínez (QC)...")
uploaded_file = st.file_uploader("Tải 1 ảnh (Phôi thẻ hoặc Efhub đã buff HLV)", type=['png', 'jpg', 'jpeg'], accept_multiple_files=False)

# ---------------------------------------------------------
# 3. LỌC RÁC KÝ TỰ & BỘ NÃO AI LOGIC VIP
# ---------------------------------------------------------
def clean_text_formatting(raw_text):
    """Xóa bỏ triệt để các ký tự rác Markdown và LaTeX"""
    text = raw_text.replace("**", "").replace("*", "").replace("$", "").replace("#", "")
    text = text.replace("\\rightarrow", "->").replace("\\Rightarrow", "=>")
    return text

def execute_tactical_analysis(image_obj, p_info, eco, manager):
    try:
        api_key = st.secrets.get("GEMINI_API_KEY")
        if not api_key: return "[LỖI CẤU HÌNH]: Không tìm thấy GEMINI_API_KEY trong Secrets!"
            
        client = genai.Client(api_key=api_key)
        
        system_instruction = """
        Bạn là DNS TACTICAL ARCHITECT - Giám đốc Kỹ thuật & Chuyên gia Phân tích eFootball Cao cấp.

        QUY TẮC ĐỊNH DẠNG (BẮT BUỘC):
        1. KHÔNG dùng dấu sao (*), dấu thăng (#), dấu đô la ($), hoặc mã LaTeX (\\rightarrow). Dùng gạch ngang (-) cho danh sách, dùng (->) chỉ hướng.
        2. CẤM TUYỆT ĐỐI dùng từ "(GIẤU)".
        3. BẮT BUỘC CHIA BÀI VIẾT THÀNH ĐÚNG 3 PHẦN BẰNG DẤU ===

        QUY TẮC PHÂN LOẠI THẺ THEO LEVEL (CỰC KỲ QUAN TRỌNG):
        
        TRƯỜNG HỢP A: Ảnh hiển thị "Level 1" (Thẻ Cố Định / Preset của Konami):
        - Tuyệt đối KHÔNG đề xuất Công thức Manual Build, KHÔNG đề xuất Booster, KHÔNG đề xuất Skill thêm.
        - Tập trung 100% đánh giá thực chiến: Bộ chỉ số Level 1 này có gánh nổi triết lý của HLV không? Vị trí & sơ đồ tối ưu nhất để tận dụng phôi thẻ cố định này. Ưu/nhược điểm khi đá PvP/SIM.

        TRƯỜNG HỢP B: Ảnh hiển thị Level > 1 (Thẻ Tùy Chỉnh):
        - Xuất Công thức Manual Build Độc quyền (Chỉ rõ điểm cộng và giải thích chuyên môn lý do nâng).
        - Chọn chính xác 1 Extra Booster (+1) từ Danh sách chuẩn bên dưới.
        - Khẳng định đề xuất TOP 5 SKILLS BỔ SUNG BẮT BUỘC (Tẩy cho 5 slot trống, KHÔNG dùng từ 'nếu có/nếu còn trống', KHÔNG TRÙNG skill gốc trong ảnh).

        DANH SÁCH EXTRA BOOSTER SLOT CHUẨN (+1 STATS):
        Accuracy +1; Aerial +1; Aerial Block +1; Agility +1; Balancer +1; Ball Protection +1; Ball-carrying +1; Breakthrough +1; Counter +1; Crossing +1; Defending +1; Duelling +1; Fantasista +1; Free-kick Taking +1; Goalkeeping +1; Hard Worker +1; Off the ball +1; Offence creator +1; Passing +1; Physicality +1; Rebuilding +1; Regista +1; Saving +1; Shooting +1; Shutdown +1; Stealing +1; Strength +1; Striker's Instinct +1; Technique +1.

        CẤU TRÚC ĐẦU RA 3 PHẦN:
        PHẦN 1: TỔNG QUAN (Trước dấu === đầu tiên)
        - Đọc vị tố chất / Triết lý HLV.
        - Vai trò thực chiến & Quỹ PP (Nếu có).

        PHẦN 2: CHIẾN THUẬT & CHỈ SỐ (Giữa 2 dấu ===)
        - Nếu có HLV: Sơ đồ tối ưu & Quy hoạch nhân sự.
        - Công thức Manual Build (Nếu Level > 1) HOẶC Định hướng vị trí tối ưu (Nếu Level 1).
        - 1 Booster (+1) + Top 5 Skill tẩy chuyên dụng (Nếu Level > 1).

        PHẦN 3: BÓC TÁCH & HIGHLIGHT (Sau dấu === cuối cùng)
        - Bóc tách điểm mù và sự lãng phí của hệ thống Auto OVR.
        - Kịch bản Highlight in-game thực chiến.
        """
        config = types.GenerateContentConfig(system_instruction=system_instruction, temperature=0.3)
        
        has_p = bool(p_info.strip())
        has_m = bool(manager.strip())
        
        if has_m and not has_p: kich_ban = "KỊCH BẢN 1: TƯ DUY KIẾN TRÚC SƯ"
        elif has_p and not has_m: kich_ban = "KỊCH BẢN 2: TUYỂN TRẠCH VIÊN"
        else: kich_ban = "KỊCH BẢN 3: DNS ÉP CHỈ SỐ"
            
        context_prompt = f"Cầu thủ: {p_info if has_p else 'Không'} | HLV: {manager if has_m else 'Không'} | Chế độ: {eco}. THỰC THI DUY NHẤT: {kich_ban}."
        
        contents = [context_prompt]
        if image_obj: contents.append(image_obj)
            
        response = client.models.generate_content(model='gemini-3.6-flash', contents=contents, config=config)
        return clean_text_formatting(response.text)
    except Exception as e:
        if "503" in str(e):
            return "[MÁY CHỦ BẬN]: Hệ thống Gemini đang quá tải tạm thời. Vui lòng bấm lại sau 5 giây."
        return f"[LỖI HỆ THỐNG]: {str(e)}"

# ---------------------------------------------------------
# 4. XỬ LÝ SỰ KIỆN & IN PHIẾU VIP (TỰ ĐỘNG CHIA TAB)
# ---------------------------------------------------------
if st.button("BẮT ĐẦU PHÂN TÍCH VIP"):
    if 'analysis_report' in st.session_state: del st.session_state['analysis_report']
        
    if not uploaded_file: st.error("Vui lòng tải 1 ảnh Phôi thẻ/HLV lên!")
    elif not player_info and not manager_name: st.error("Vui lòng nhập tên Cầu thủ hoặc HLV!")
    else:
        with st.spinner("Hệ thống DNS đang trích xuất Báo cáo VIP..."):
            img = Image.open(uploaded_file)
            img.thumbnail((800, 800))
            
            report = execute_tactical_analysis(img, player_info, ecosystem, manager_name)
            st.session_state['analysis_report'] = report
            
            del img
            gc.collect()

# --- HIỂN THỊ DẠNG TABS ---
if 'analysis_report' in st.session_state:
    report_text = st.session_state['analysis_report']
    
    parts = report_text.split("===")
    
    tab1_content = parts[0] if len(parts) > 0 else "Đang cập nhật dữ liệu..."
    tab2_content = parts[1] if len(parts) > 1 else "Vui lòng xem thông tin ở Tab Tổng Quan."
    tab3_content = parts[2] if len(parts) > 2 else "Vui lòng xem thông tin ở Tab Tổng Quan."
    
    tab1, tab2, tab3 = st.tabs(["📋 TỔNG QUAN", "⚙️ CHIẾN THUẬT", "🚀 ĐÁNH GIÁ"])
    
    LINK_LOGO = "https://i.postimg.cc/4KNSdqRd/D9754823-56B4-4957-8F90-1EE072CFF5A2.jpg"
    
    def format_tab(content):
        return f"""
        <div class="vip-card">
            <div style="text-align:center; margin-bottom: 15px;">
                <img src="{LINK_LOGO}" style="max-width: 90px; border-radius: 8px;">
            </div>
            <div class="vip-text">{content.strip()}</div>
            <div class="vip-footer">
                <span style="color: #FFD700; font-weight: bold; font-size: 13px;">DNS TACTICAL ARCHITECT</span><br>
                © 2026 DN SIM MY LEAGUE. All rights reserved.
            </div>
        </div>
        """

    with tab1:
        st.markdown(format_tab(tab1_content), unsafe_allow_html=True)
    with tab2:
        st.markdown(format_tab(tab2_content), unsafe_allow_html=True)
    with tab3:
        st.markdown(format_tab(tab3_content), unsafe_allow_html=True)
        
    with st.expander("Bấm vào đây để Copy văn bản thô (Dành cho Team Content)"):
        st.text_area("Văn bản gốc:", value=report_text.replace("===", "\n\n"), height=200)
