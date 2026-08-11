import streamlit as st
from PIL import Image
from google import genai
from google.genai import types
import os

# ---------------------------------------------------------
# CẤU HÌNH GIAO DIỆN CHUNG
# ---------------------------------------------------------
st.set_page_config(page_title="DNS TACTICAL ARCHITECT", page_icon="🛡️", layout="wide")

custom_css = """
<style>
    .stTextArea textarea { height: 400px !important; font-family: 'Consolas', monospace !important; font-size: 16px !important; background-color: #0f1923 !important; color: #00ffcc !important; }
    .stButton > button { width: 100%; height: 60px; font-size: 20px; font-weight: bold; background-color: #1a365d; color: white; }
    .stButton > button:hover { background-color: #2b6cb0; }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)
st.markdown("<h1 style='text-align: center; color: #2b6cb0;'>DNS TACTICAL ARCHITECT</h1>", unsafe_allow_html=True)

# ---------------------------------------------------------
# KHỐI NHẬP LIỆU (UI)
# ---------------------------------------------------------
col1, col2 = st.columns(2)
with col1:
    player_info = st.text_input("Tên Cầu thủ & Vị trí (Bỏ trống nếu muốn vẽ sơ đồ HLV):", placeholder="Ví dụ: D. Bergkamp - CF")
    ecosystem = st.selectbox("Chọn hệ sinh thái (SIM AI / PvP):", ["SIM AI", "PvP"])
with col2:
    manager_name = st.text_input("Tên HLV (Bỏ trống nếu muốn khám bệnh Cầu thủ):", placeholder="Ví dụ: Xabi Alonso (Quick Counter)")
    uploaded_files = st.file_uploader("Tải ảnh (Phôi thẻ Cầu thủ HOẶC HLV)", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)

# ---------------------------------------------------------
# BỘ LUẬT LỆ PHÂN MẢNH (CHỈ NẠP 1 TRONG 3 LUẬT VÀO AI)
# ---------------------------------------------------------
# Định dạng chuẩn bắt buộc cho mọi kịch bản
BASE_RULES = """
Bạn là DNS TACTICAL ARCHITECT - Giám đốc Kỹ thuật (Technical Director) kiêm Bậc thầy Chiến thuật eFootball.
LỜI NÓI CỦA BẠN LÀ CHÂN LÝ: đanh thép, chuyên nghiệp, uy quyền. TUYỆT ĐỐI KHÔNG nói bừa, không dùng từ "có lẽ", "tùy thuộc".
LỆNH TỐI THƯỢNG:
1. VĂN BẢN SIÊU PHẲNG. TUYỆT ĐỐI KHÔNG dùng Markdown. Phân tách mục bằng ngoặc vuông []. KHÔNG lời chào.
2. TUYỆT ĐỐI KHÔNG BAO GIỜ SỬ DỤNG TỪ "(GIẤU)". KHÔNG viết Content MXH.
\n\nBẠN BẮT BUỘC PHẢI THỰC THI CHÍNH XÁC CÁC MỤC SAU ĐÂY, KHÔNG ĐƯỢC THÊM BỚT BẤT KỲ MỤC NÀO KHÁC:\n
"""

# Luật cho Kịch bản 1: Chỉ có HLV
RULE_SCENARIO_1 = BASE_RULES + """
[PHÂN TÍCH TRIẾT LÝ HLV] Đánh giá Lối chơi và Manager Boosts bằng góc nhìn sắc bén.
[SƠ ĐỒ TỐI ƯU] Phán quyết 1 sơ đồ chiến thuật (VD: 4-2-1-3) phù hợp nhất.
[QUY HOẠCH DREAM TEAM 23 NHÂN SỰ] Liệt kê 11 đá chính và 12 dự bị. Format: "Vị trí - Playstyle bắt buộc". TUYỆT ĐỐI KHÔNG đề xuất tên cầu thủ cụ thể.
[THIẾT LẬP LỆNH CÁ NHÂN] Chỉ định rõ Lệnh Tấn Công, Phòng Ngự, Mặc Định.
"""

# Luật cho Kịch bản 2: Chỉ có Cầu thủ
RULE_SCENARIO_2 = BASE_RULES + """
[ĐỌC VỊ TỐ CHẤT CẦU THỦ] Bóc tách điểm mạnh/yếu chí mạng không khoan nhượng.
[ĐỊNH HƯỚNG LỐI CHƠI] Phán quyết phôi thẻ hợp với Style HLV nào nhất. Đề xuất HLV phù hợp.
"""

# Luật cho Kịch bản 3: Có cả Cầu thủ và HLV
RULE_SCENARIO_3 = BASE_RULES + """
[THẨM ĐỊNH TƯƠNG THÍCH CHIẾN THUẬT] Đánh giá sự phù hợp giữa Playstyle của phôi thẻ và Lối chơi của HLV. Nếu lệch pha, phải chỉ trích chuyên môn.
[BẢNG TÍNH TOÁN PP NGẦM] Quét "Points X / Y". Lấy Y làm TỔNG QUỸ PP. Nếu cắt ảnh, tự suy luận quỹ tối đa. Tính toán tiêu hao PP (1-4:1, 5-8:2, 9-12:3, 13-16:4).
[CÔNG THỨC MANUAL BUILD] Chốt hạ 1 dòng (VD: Shooting: 4, Passing: 6...). Đảm bảo phân bổ hết quỹ PP.
[QUY HOẠCH BOOSTER SLOT 2] Quét kỹ 'Level Cap' và biểu tượng Booster:
- Nếu Cap=1, hoặc không có Booster, hoặc có 2 Booster sáng: TUYỆT ĐỐI KHÔNG ĐỀ XUẤT.
- CHỈ KHI Level Cap>1 VÀ có 1 khe Booster sáng kèm 1 khe trống/mờ: BẮT BUỘC đề xuất 1 Token từ các nhóm sau (CẤM BỊA TÊN):
  + Tấn công/Kỹ thuật: Technique, Fantasista, Breakthrough, Ball-carrying, Offence creator, Passing, Crossing, Accuracy, Free-kick Taking, Striker's Instinct, Off the ball, Shooting.
  + Thể chất: Agility, Balancer, Ball Protection, Hard Worker, Physicality, Strength, Aerial.
  + Phòng ngự: Defending, Duelling, Shutdown, Stealing, Rebuilding, Regista, Counter, Aerial Block.
  + GK: Goalkeeping, Saving.
Giải thích ngắn gọn (1 câu đanh thép) lý do chọn Token để bù đắp điểm yếu của Manual Build.
[TOP 5 SKILL SINH TỒN BỔ SUNG] 5 skill cách nhau dấu phẩy (Cấm gán sút cho GK. Cần sút xa ghi 'Long-range Shooting').
[ĐỐI CHIẾU AUTO VS THỦ CÔNG] 1 đoạn văn siêu phẳng chỉ trích Auto OVR và khẳng định tính vượt trội của công thức Thủ công.
"""

# ---------------------------------------------------------
# HÀM XỬ LÝ CHÍNH
# ---------------------------------------------------------
def execute_tactical_analysis(image_objs, p_info, eco, manager):
    try:
        client = genai.Client()
        
        has_player = bool(p_info.strip())
        has_manager = bool(manager.strip())
        
        # PYTHON QUYẾT ĐỊNH LUẬT LỆ NÀO ĐƯỢC NẠP VÀO AI
        if has_manager and not has_player:
            active_instruction = RULE_SCENARIO_1
            context_prompt = f"Yêu cầu: Phân tích HLV: {manager}. Sinh thái: {eco}."
        elif has_player and not has_manager:
            active_instruction = RULE_SCENARIO_2
            context_prompt = f"Yêu cầu: Khám bệnh Cầu thủ: {p_info}. Sinh thái: {eco}."
        else: # Có cả hai
            active_instruction = RULE_SCENARIO_3
            context_prompt = f"Yêu cầu: Ép chỉ số Cầu thủ: {p_info} cho HLV: {manager}. Sinh thái: {eco}."
            
        config = types.GenerateContentConfig(
            system_instruction=active_instruction, 
            temperature=0.1
        )
        
        contents = [context_prompt]
        if image_objs:
            contents.extend(image_objs)
            
        response = client.models.generate_content(
            model='gemini-3.6-flash',
            contents=contents,
            config=config
        )
        return response.text
    except Exception as e:
        return f"[LỖI HỆ THỐNG]: {str(e)}"

# ---------------------------------------------------------
# XỬ LÝ SỰ KIỆN NÚT BẤM
# ---------------------------------------------------------
if st.button("[XỬ LÝ DỮ LIỆU]"):
    if not uploaded_files:
        st.error("LỖI CẤP CAO: Bạn BẮT BUỘC phải tải lên ít nhất 1 ảnh (Phôi thẻ hoặc HLV)!")
    elif not player_info and not manager_name:
        st.error("LỖI CẤP CAO: Bạn phải nhập tên Cầu thủ (để ép chỉ số) HOẶC tên HLV (để vẽ sơ đồ)!")
    else:
        with st.spinner("Giám đốc Kỹ thuật đang thiết lập chiến thuật..."):
            images = [Image.open(f) for f in uploaded_files]
            analysis_result = execute_tactical_analysis(images, player_info, ecosystem, manager_name)
            st.session_state['analysis_report'] = analysis_result

if 'analysis_report' in st.session_state:
    st.text_area(label="KẾT QUẢ R&D (Copy dán TikTok/Facebook...):", value=st.session_state['analysis_report'], key="flat_text_display")