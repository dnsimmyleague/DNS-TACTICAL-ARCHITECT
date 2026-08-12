import streamlit as st
from PIL import Image
from google import genai
from google.genai import types
import random
import gc

# ---------------------------------------------------------
# CẤU HÌNH GIAO DIỆN CHUNG - VIP DNS (HỖ TRỢ AUTO SÁNG/TỐI)
# ---------------------------------------------------------
st.set_page_config(page_title="DN SIM MY LEAGUE | VIP DNS", page_icon="👑", layout="centered")

custom_css = """
<style>
    /* 1. Xóa sạch dấu vết của Streamlit */
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    
    /* 2. Tiêu đề Thương hiệu */
    .title-brand { 
        text-align: center; 
        color: #D4AF37; 
        font-size: 2.2rem; 
        font-weight: 900; 
        margin-bottom: 5px; 
        letter-spacing: 2px; 
    }
    
    .slogan { 
        text-align: center; 
        color: #888888; 
        font-size: 1rem; 
        font-style: italic; 
        margin-bottom: 25px; 
    }

    /* 3. Nút bấm phẳng, mạnh mẽ */
    .stButton > button { 
        width: 100%; height: 55px; font-size: 18px; font-weight: 900; 
        background-color: #D4AF37; color: #121418 !important; border: none; border-radius: 8px; 
    }

    /* 4. HIỆU ỨNG TAB 3D (KẸP HỒ SƠ) */
    .stTabs [data-baseweb="tab-list"] { 
        gap: 8px; 
    }
    .stTabs [data-baseweb="tab"] { 
        background-color: rgba(212, 175, 55, 0.05); /* Màu nền mờ khi chưa chọn */
        border: 1px solid rgba(212, 175, 55, 0.4);
        border-bottom: none;
        border-radius: 8px 8px 0px 0px; /* Bo tròn góc trên như folder */
        padding: 10px 15px; 
        box-shadow: inset 0 -3px 5px rgba(0,0,0,0.02); /* Đổ bóng chìm */
        transition: all 0.2s ease-in-out;
    }
    
    /* Khi Tab được bấm (Nhô lên, đổi màu) */
    .stTabs [aria-selected="true"] { 
        background-color: #D4AF37 !important; 
        color: #121418 !important; 
        font-weight: 900;
        transform: translateY(-2px); /* Hiệu ứng nhô cao lên */
        box-shadow: 0 -4px 10px rgba(0,0,0,0.1); /* Đổ bóng nổi */
        border: 1px solid #D4AF37;
    }
    
    /* 5. Khung Báo Cáo nối liền với Tab */
    .vip-card { 
        background-color: var(--background-color); /* Tự động đổi Sáng/Tối theo thiết bị */
        border: 2px solid #D4AF37; 
        border-radius: 0px 10px 10px 10px; 
        padding: 20px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.05);
    }
    
    .vip-text { 
        font-family: monospace; 
        font-size: 14px; 
        line-height: 1.6; 
        white-space: pre-wrap; 
        color: var(--text-color); /* Tự động đổi chữ đen/trắng theo nền */
    }
    
    .vip-footer { 
        text-align: center; 
        border-top: 1px dashed #D4AF37; 
        padding-top: 15px; 
        margin-top: 20px; 
        color: #888888; 
        font-size: 12px; 
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# Hiển thị Tiêu đề và Slogan
st.markdown("<h1 class='title-brand'>DN SIM MY LEAGUE</h1>", unsafe_allow_html=True)
st.markdown("<p class='slogan'>Giải Mã Sơ Đồ - Định Hình Meta - Kiến Tạo Dream Team</p>", unsafe_allow_html=True)

# ---------------------------------------------------------
# KHỐI NHẬP LIỆU
# ---------------------------------------------------------
player_info = st.text_input("Tên Cầu thủ & Vị trí (Bỏ trống nếu vẽ sơ đồ):", placeholder="Ví dụ: D. Bergkamp - CF")
ecosystem = st.selectbox("Chọn hệ sinh thái (SIM AI / PvP):", ["SIM AI", "PvP"])
manager_name = st.text_input("Tên HLV (Bỏ trống nếu khám bệnh cầu thủ):", placeholder="Ví dụ: R. Martínez (QC)...")
uploaded_file = st.file_uploader("Tải 1 ảnh (Phôi thẻ/HLV)", type=['png', 'jpg', 'jpeg'], accept_multiple_files=False)

# ---------------------------------------------------------
# LÕI TRÍ TUỆ NHÂN TẠO (AI CORE)
# ---------------------------------------------------------
def execute_tactical_analysis(image_obj, p_info, eco, manager):
    try:
        api_key = st.secrets.get("GEMINI_API_KEY")
        if not api_key: return "[LỖI]: Không tìm thấy mã API."
            
        client = genai.Client(api_key=api_key)
        
        system_instruction = """
        Bạn là DNS TACTICAL ARCHITECT. Viết Báo cáo nội bộ VIP. Không dùng từ "(GIẤU)".
        LỆNH QUAN TRỌNG NHẤT: BẠN BẮT BUỘC PHẢI CHIA BÀI VIẾT THÀNH ĐÚNG 3 PHẦN. 
        Giữa mỗi phần, bạn phải đặt 1 dòng chỉ chứa duy nhất ký hiệu này: ===
        
        PHẦN 1: TỔNG QUAN (Trước dấu === đầu tiên)
        - Đọc vị tố chất / Triết lý HLV.
        - Vai trò thực chiến & Quỹ PP (Nếu có).
        
        PHẦN 2: CHIẾN THUẬT & CHỈ SỐ (Giữa 2 dấu ===)
        - Nếu có HLV: Sơ đồ tối ưu & Quy hoạch nhân sự.
        - Nếu có cầu thủ: Công thức Manual Build Độc quyền (Giải thích chi tiết). 
        - Đề xuất Booster & Skill KHÔNG TRÙNG trong ảnh.
        
        PHẦN 3: BÓC TÁCH & HIGHLIGHT (Sau dấu === cuối cùng)
        - Phân tích điểm mù và sự lãng phí của hệ thống AUTO OVR.
        - Vẽ kịch bản Highlight in-game.
        """
        config = types.GenerateContentConfig(system_instruction=system_instruction, temperature=0.3)
        
        has_p = bool(p_info.strip())
        has_m = bool(manager.strip())
        
        if has_m and not has_p: kich_ban = "KỊCH BẢN 1: TƯ DUY KIẾN TRÚC SƯ"
        elif has_p and not has_m: kich_ban = "KỊCH BẢN 2: TUYỂN TRẠCH VIÊN"
        else: kich_ban = "KỊCH BẢN 3: DNS ÉP CHỈ SỐ - CONTENT TRIỆU VIEW"
            
        context_prompt = f"Cầu thủ: {p_info if has_p else 'Không'} | HLV: {manager if has_m else 'Không'} | Chế độ: {eco}. THỰC THI DUY NHẤT: {kich_ban}."
        
        contents = [context_prompt]
        if image_obj: contents.append(image_obj)
            
        response = client.models.generate_content(model='gemini-3.6-flash', contents=contents, config=config)
        return response.text
    except Exception as e:
        return f"[LỖI HỆ THỐNG]: {str(e)}"

# ---------------------------------------------------------
# XỬ LÝ SỰ KIỆN VÀ CHIA TAB GIAO DIỆN
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
    
    # Định dạng HTML bọc nội dung từng Tab, chèn thêm link Logo để nhận diện
    LINK_LOGO = "https://i.postimg.cc/4KNSdqRd/D9754823-56B4-4957-8F90-1EE072CFF5A2.jpg"
    
    def format_tab(content):
        return f"""
        <div class="vip-card">
            <div style="text-align:center; margin-bottom: 15px;">
                <img src="{LINK_LOGO}" style="max-width: 100px; border-radius: 8px;">
            </div>
            <div class="vip-text">{content.strip()}</div>
            <div class="vip-footer">
                <span style="color: #D4AF37; font-weight: bold;">DN SIM MY LEAGUE</span><br>
                © 2026 Bản quyền phân tích Độc quyền (VIP DNS)
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
