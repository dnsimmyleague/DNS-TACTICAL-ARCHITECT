import streamlit as st
from PIL import Image
from google import genai
from google.genai import types
import gc

# ---------------------------------------------------------
# 1. CẤU HÌNH GIAO DIỆN MỆNH KIM PREMIUM 
# ---------------------------------------------------------
st.set_page_config(page_title="DN SIM MY LEAGUE | VIP DNS", page_icon="👑", layout="centered")

custom_css = """
<style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .stApp { background-color: #1E222A !important; }
    
    .title-brand { 
        text-align: center; color: #FFD700 !important; font-size: 2.4rem; 
        font-weight: 900; margin-bottom: 5px; letter-spacing: 2px;
        text-shadow: 0px 2px 10px rgba(255, 215, 0, 0.3);
    }
    .slogan { text-align: center; color: #E0E6ED !important; font-size: 1.05rem; font-style: italic; margin-bottom: 25px; }

    .stTextInput > div > div > input, .stSelectbox > div > div > div {
        background-color: #F4F6F9 !important; color: #111827 !important;
        font-weight: 600 !important; border-radius: 8px !important; border: 1px solid #D4AF37 !important;
    }
    label, .stCheckbox > label > div > p { color: #FFD700 !important; font-weight: bold !important; font-size: 15px !important;}

    .stButton > button { 
        width: 100%; height: 55px; font-size: 19px; font-weight: 900; 
        background: linear-gradient(135deg, #FFD700 0%, #D4AF37 100%) !important; 
        color: #121418 !important; border: none !important; border-radius: 8px !important;
        box-shadow: 0 4px 12px rgba(212, 175, 55, 0.4);
    }

    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { 
        background-color: #2A2F3A !important; border: 1px solid #D4AF37 !important;
        border-bottom: none !important; border-radius: 8px 8px 0px 0px !important; padding: 10px 16px !important; color: #E0E6ED !important;
    }
    .stTabs [aria-selected="true"] { 
        background-color: #FFD700 !important; color: #121418 !important; 
        font-weight: 900 !important; transform: translateY(-3px); box-shadow: 0 -4px 10px rgba(255, 215, 0, 0.3);
    }
    
    .vip-card { 
        background-color: #252A34 !important; border: 2px solid #FFD700 !important; 
        border-radius: 0px 10px 10px 10px; padding: 22px; box-shadow: 0 6px 20px rgba(0,0,0,0.3);
    }
    .vip-text { font-family: 'Consolas', monospace; font-size: 14.5px; line-height: 1.6; white-space: pre-wrap; color: #F3F4F6 !important; }
    .vip-footer { text-align: center; border-top: 1px dashed #FFD700; padding-top: 15px; margin-top: 20px; color: #9CA3AF; font-size: 12px; }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)
st.markdown("<h1 class='title-brand'>DN SIM MY LEAGUE</h1>", unsafe_allow_html=True)
st.markdown("<p class='slogan'>Giải Mã Sơ Đồ - Định Hình Meta - Kiến Tạo Dream Team</p>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. KHỐI NHẬP LIỆU (CƠ CHẾ MỞ KHÓA TỰ DO)
# ---------------------------------------------------------
player_info = st.text_input("Tên Cầu thủ/Sơ đồ (Bỏ trống nếu không cần):", placeholder="Ví dụ: D. Bergkamp hoặc 4-2-1-3")
ecosystem = st.selectbox("Chọn hệ sinh thái (SIM AI / PvP):", ["SIM AI", "PvP"])
is_comparison = st.checkbox("✅ ĐÂY LÀ ẢNH SO SÁNH CẦU THỦ (Trái: AUTO | Phải: MANUAL DNS)")

st.markdown("<p style='color: #FFD700; font-weight: bold; margin-bottom: 0px;'>📸 1. Tải ảnh Cầu thủ (Phôi thẻ gốc HOẶC Ảnh so sánh 2 cột):</p>", unsafe_allow_html=True)
uploaded_player = st.file_uploader("", type=['png', 'jpg', 'jpeg'], key="player_img")

st.markdown("<p style='color: #FFD700; font-weight: bold; margin-bottom: 0px;'>📸 2. Tải ảnh HLV (Để phân tích Dream Team hoặc Buff cộng hưởng):</p>", unsafe_allow_html=True)
uploaded_manager = st.file_uploader("", type=['png', 'jpg', 'jpeg'], key="manager_img")

# ---------------------------------------------------------
# 3. BỘ NÃO AI LOGIC VIP (XỬ LÝ DỮ LIỆU ĐA KỊCH BẢN)
# ---------------------------------------------------------
def clean_text(raw_text):
    text = raw_text.replace("**", "").replace("*", "").replace("$", "").replace("#", "")
    return text.replace("\\rightarrow", "->").replace("\\Rightarrow", "=>")

def execute_tactical_analysis(img_player, img_manager, p_info, eco, is_comp):
    try:
        api_key = st.secrets.get("GEMINI_API_KEY")
        if not api_key: return "[LỖI CẤU HÌNH]: Không tìm thấy GEMINI_API_KEY!"
            
        client = genai.Client(api_key=api_key)
        
        system_instruction = """
        Bạn là DNS TACTICAL ARCHITECT - Chuyên gia Phân tích Chiến thuật eFootball VIP quốc tế.

        QUY TẮC ĐỊNH DẠNG & VĂN PHONG:
        1. KHÔNG dùng ký tự Markdown (*, #, $, \\rightarrow). Dùng gạch ngang (-) cho danh sách, mũi tên (->) chỉ hướng.
        2. NGHIÊM CẤM dùng tiếng lóng (đè C, chọc ngoáy, ảo ma, phế...). Không dùng từ "(GIẤU)". Chỉ dùng ngôn ngữ phân tích VIP.
        3. BẮT BUỘC CHIA BÀI VIẾT THÀNH ĐÚNG 3 PHẦN BẰNG KÝ HIỆU ===

        XÁC ĐỊNH KỊCH BẢN LÀM VIỆC DỰA TRÊN ẢNH ĐẦU VÀO:
        
        KỊCH BẢN A: CHỈ CÓ ẢNH HLV (KHÔNG CÓ ẢNH CẦU THỦ) - KIẾN TẠO DREAM TEAM
        - PHẦN 1 (Trước ===): TỔNG QUAN TRIẾT LÝ. Đọc vị lối chơi HLV, phân tích Link-up Play (nếu có) và đề xuất sơ đồ chiến thuật tối ưu nhất.
        - PHẦN 2 (Giữa ===): QUY HOẠCH 23 NHÂN SỰ. Chỉ định vị trí và Playstyle bắt buộc cho 11 người đá chính và 12 dự bị (Ví dụ: CF - Goal Poacher, DMF - Anchor Man).
        - PHẦN 3 (Sau ===): INDIVIDUAL INSTRUCTIONS & KỊCH BẢN THAY NGƯỜI.
            + Mặc định: Đề xuất Individual Instructions cho 11 người đá chính (Anchoring, Defensive, Counter Target...).
            + Tấn công tất tay (Bị dẫn bàn): Đề xuất thay ai, vai trò gì, cài Instruction gì.
            + Bảo toàn tỉ số (Thủ): Đề xuất thay ai, vai trò gì, cài Instruction gì.

        KỊCH BẢN B: CÓ ẢNH CẦU THỦ (CÓ HOẶC KHÔNG CÓ HLV KÈM THEO)
        - Nếu có HLV kèm theo, lấy thông số Buff/Link-up của HLV để trừ hao điểm PP và thiết kế lối chơi cộng hưởng.
        - Nếu là ẢNH SO SÁNH KÉP (Trái: Auto, Phải: Manual): Phản biện sự lãng phí của Auto, bảo vệ bản Manual dựa trên chiến thuật. Tuyệt đối không tự bịa số.
        - Nếu là Cầu thủ Level 1: Chỉ đánh giá thực chiến, vị trí tối ưu.
        - Nếu là Cầu thủ Build tay (Level > 1): Xuất Công thức Manual. Chọn 1 Booster (+1). Xuất TOP 5 SKILL BỔ SUNG: Xếp thứ tự ưu tiên 1 đến 5 (1 là quan trọng nhất). Không dùng từ ngập ngừng.

        DANH SÁCH EXTRA BOOSTER (+1): Accuracy, Aerial, Aerial Block, Agility, Balancer, Ball Protection, Ball-carrying, Breakthrough, Counter, Crossing, Defending, Duelling, Fantasista, Free-kick Taking, Goalkeeping, Hard Worker, Off the ball, Offence creator, Passing, Physicality, Rebuilding, Regista, Saving, Shooting, Shutdown, Stealing, Strength, Striker's Instinct, Technique.
        """
        config = types.GenerateContentConfig(system_instruction=system_instruction, temperature=0.3)
        
        comp_text = "ĐÂY LÀ ẢNH SO SÁNH CẦU THỦ (TRÁI LÀ AUTO, PHẢI LÀ MANUAL). Hãy phản biện Auto và bảo vệ Manual." if is_comp else ""
        context_prompt = f"Thông tin/Sơ đồ: {p_info} | Chế độ: {eco}. {comp_text}"
        
        contents = [context_prompt]
        if img_player: contents.append(img_player)
        if img_manager: contents.append(img_manager)
            
        response = client.models.generate_content(model='gemini-3.6-flash', contents=contents, config=config)
        return clean_text(response.text)
    except Exception as e:
        if "503" in str(e): return "[MÁY CHỦ BẬN]: Hệ thống Gemini quá tải tạm thời. Vui lòng thử lại sau 5 giây."
        return f"[LỖI HỆ THỐNG]: {str(e)}"

# ---------------------------------------------------------
# 4. XỬ LÝ SỰ KIỆN & IN PHIẾU VIP (CHIA TAB)
# ---------------------------------------------------------
if st.button("BẮT ĐẦU PHÂN TÍCH VIP"):
    # Cập nhật Logic: Cho phép chạy nếu có BẤT KỲ ảnh nào (Cầu thủ hoặc HLV)
    if not uploaded_player and not uploaded_manager: 
        st.error("Vui lòng tải ít nhất 1 ảnh Cầu thủ ở mục 1 HOẶC 1 ảnh HLV ở mục 2!")
    else:
        with st.spinner("Hệ thống DNS đang trích xuất Báo cáo VIP..."):
            img_p = None
            img_m = None
            
            if uploaded_player:
                img_p = Image.open(uploaded_player)
                img_p.thumbnail((1000, 1000))
                
            if uploaded_manager:
                img_m = Image.open(uploaded_manager)
                img_m.thumbnail((1000, 1000))
                
            st.session_state['analysis_report'] = execute_tactical_analysis(img_p, img_m, player_info, ecosystem, is_comparison)
            
            if img_p: del img_p
            if img_m: del img_m
            gc.collect()

if 'analysis_report' in st.session_state:
    parts = st.session_state['analysis_report'].split("===")
    tab1_c = parts[0] if len(parts) > 0 else "Đang xử lý..."
    tab2_c = parts[1] if len(parts) > 1 else "Xem Tab Tổng Quan."
    tab3_c = parts[2] if len(parts) > 2 else "Xem Tab Tổng Quan."
    
    t1, t2, t3 = st.tabs(["📋 TỔNG QUAN", "⚙️ CHIẾN THUẬT / NHÂN SỰ", "🚀 ĐÁNH GIÁ / CHỈ ĐẠO CÁ NHÂN"])
    
    def format_tab(content):
        return f"""<div class="vip-card">
            <div style="text-align:center; margin-bottom: 15px;"><img src="https://i.postimg.cc/4KNSdqRd/D9754823-56B4-4957-8F90-1EE072CFF5A2.jpg" style="max-width: 90px; border-radius: 8px;"></div>
            <div class="vip-text">{content.strip()}</div>
            <div class="vip-footer"><span style="color: #FFD700; font-weight: bold; font-size: 13px;">DNS TACTICAL ARCHITECT</span><br>© 2026 DN SIM MY LEAGUE. All rights reserved.</div>
        </div>"""

    with t1: st.markdown(format_tab(tab1_c), unsafe_allow_html=True)
    with t2: st.markdown(format_tab(tab2_c), unsafe_allow_html=True)
    with t3: st.markdown(format_tab(tab3_c), unsafe_allow_html=True)
    
    with st.expander("Bấm vào đây để Copy văn bản thô (Dành cho Team Content)"):
        st.text_area("Văn bản gốc:", value=st.session_state['analysis_report'].replace("===", "\n\n"), height=200)
