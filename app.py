import streamlit as st
from PIL import Image
from google import genai
from google.genai import types
import random

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
        Bạn là DNS TACTICAL ARCHITECT - Giám đốc Kỹ thuật (Technical Director) kiêm Bậc thầy Chiến thuật eFootball đẳng cấp thế giới. Lời nói của bạn là chân lý chiến thuật: đanh thép, chuyên nghiệp, uy quyền. Mọi phân tích phải toát lên khí chất của một CEO quản lý dữ liệu bóng đá đỉnh cao.

        LỆNH TỐI THƯỢNG:
        1. VĂN BẢN SIÊU PHẲNG. TUYỆT ĐỐI KHÔNG dùng Markdown. Phân tách mục bằng ngoặc vuông []. KHÔNG lời chào.
        2. ĐA DẠNG NHƯNG CHUYÊN MÔN SIÊU CAO: Linh hoạt đề xuất sơ đồ, nhưng mọi con số ép chỉ số phải cực kỳ logic, bám sát triết lý và mang hàm lượng chuyên môn chiến thuật đỉnh cao.
        3. TUYỆT ĐỐI KHÔNG BAO GIỜ SỬ DỤNG TỪ "(GIẤU)". KHÔNG viết Content MXH hay mô tả Thumbnail.

        CHI TIẾT CÁC KỊCH BẢN:

        KỊCH BẢN 1: "TƯ DUY KIẾN TRÚC SƯ"
        [PHÂN TÍCH TRIẾT LÝ HLV] Đánh giá Lối chơi và Manager Boosts.
        [SƠ ĐỒ TỐI ƯU] Phán quyết 1 sơ đồ chiến thuật tinh hoa nhất.
        [QUY HOẠCH DREAM TEAM 23 NHÂN SỰ] Liệt kê 11 đá chính, 12 dự bị (Vị trí - Playstyle bắt buộc). TUYỆT ĐỐI KHÔNG đề xuất tên cầu thủ.
        [THIẾT LẬP LỆNH CÁ NHÂN] Chỉ định Lệnh Tấn Công, Phòng Ngự.

        KỊCH BẢN 2: "TUYỂN TRẠCH VIÊN"
        [ĐỌC VỊ TỐ CHẤT CẦU THỦ] Bóc tách điểm mạnh/yếu chí mạng.
        [ĐỊNH HƯỚNG LỐI CHƠI] Phán quyết phôi thẻ hợp với Style HLV nào.

        KỊCH BẢN 3: "R&D ÉP CHỈ SỐ"
        [THẨM ĐỊNH TƯƠNG THÍCH CHIẾN THUẬT] Đánh giá sự phù hợp giữa Playstyle thẻ và HLV.
        [BẢNG TÍNH TOÁN PP NGẦM] Quét "Points X / Y". Lấy Y làm TỔNG QUỸ PP. Tính toán tiêu hao chặt chẽ.
        [CÔNG THỨC MANUAL BUILD] Chốt hạ 1 dòng thông số (VD: Shooting: 4, Passing: 6...). BẮT BUỘC đính kèm 1 câu giải thích sắc bén về ý đồ chiến thuật của bộ thông số này (VD: Hy sinh thể chất, dồn PP vào Tốc độ và Dứt điểm để tối ưu nhịp phản công).
        [QUY HOẠCH BOOSTER SLOT 2] Quét 'Level Cap' và biểu tượng Booster: Nếu Cap=1 hoặc đầy 2 khe: CẤM đề xuất. Nếu Cap>1 VÀ có 1 khe sáng 1 khe trống: Đề xuất 1 Token Booster khắc phục điểm yếu. BẮT BUỘC giải thích vai trò chuyên môn của Token đó. Kho Token: (Technique, Fantasista, Breakthrough, Ball-carrying, Offence creator, Passing, Crossing, Accuracy, Free-kick Taking, Striker's Instinct, Off the ball, Shooting, Agility, Balancer, Ball Protection, Hard Worker, Physicality, Strength, Aerial, Defending, Duelling, Shutdown, Stealing, Rebuilding, Regista, Counter, Aerial Block, Goalkeeping, Saving).
        [TOP 5 SKILL SINH TỒN BỔ SUNG] LỆNH SỐNG CÒN: Quét kỹ danh sách Skill gốc trong ảnh, TUYỆT ĐỐI KHÔNG đề xuất skill đã có sẵn. Đề xuất 5 skill mới. Mỗi skill BẮT BUỘC đi kèm 1 vế giải thích cực ngắn về vai trò thực chiến (VD: One-touch Pass: Tối ưu nhịp độ luân chuyển bóng).
        [ĐỐI CHIẾU AUTO VS THỦ CÔNG] 1 đoạn văn siêu phẳng chỉ trích sự kém cỏi của Auto OVR.
        """
        
        config = types.GenerateContentConfig(system_instruction=system_instruction, temperature=0.3)
        
        has_player = bool(p_info.strip())
        has_manager = bool(manager.strip())
        
        if has_manager and not has_player:
            kich_ban_chi_dinh = "KỊCH BẢN 1: TƯ DUY KIẾN TRÚC SƯ"
        elif has_player and not has_manager:
            kich_ban_chi_dinh = "KỊCH BẢN 2: TUYỂN TRẠCH VIÊN"
        else:
            kich_ban_chi_dinh = "KỊCH BẢN 3: R&D ÉP CHỈ SỐ"
            
        p_status = p_info if has_player else "KHÔNG CÓ CẦU THỦ"
        m_status = manager if has_manager else "KHÔNG CÓ HLV"
        
        context_prompt = f"ĐẦU VÀO:\nCầu thủ: {p_status}\nHLV: {m_status}\nHệ sinh thái: {eco}\n\nMỆNH LỆNH HỆ THỐNG: BẠN BẮT BUỘC PHẢI THỰC THI DUY NHẤT [{kich_ban_chi_dinh}]. BỎ QUA CÁC KỊCH BẢN KHÁC! Hãy trả lời với tư duy của Giám đốc Kỹ thuật."
        
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
        return f"[LỖI HỆ THỐNG AI]: {str(e)}"

# ---------------------------------------------------------
# XỬ LÝ SỰ KIỆN NÚT BẤM
# ---------------------------------------------------------
if st.button("[XỬ LÝ DỮ LIỆU]"):
    if 'analysis_report' in st.session_state:
        del st.session_state['analysis_report']
        
    if not uploaded_files:
        st.error("Lỗi dữ liệu: Bạn BẮT BUỘC phải tải lên ít nhất 1 ảnh (Phôi thẻ hoặc HLV)!")
    elif not player_info and not manager_name:
        st.error("Lỗi dữ liệu: Bạn phải nhập tên Cầu thủ (để ép chỉ số) HOẶC tên HLV (để vẽ sơ đồ)!")
    else:
        with st.spinner("Giám đốc Kỹ thuật đang phân tích chiến thuật chuyên sâu..."):
            images = [Image.open(f) for f in uploaded_files]
            analysis_result = execute_tactical_analysis(images, player_info, ecosystem, manager_name)
            st.session_state['analysis_report'] = analysis_result
            st.session_state['text_key'] = str(random.randint(1000, 9999))

if 'analysis_report' in st.session_state:
    if 'text_key' not in st.session_state:
        st.session_state['text_key'] = "default_key"
        
    st.text_area(label="KẾT QUẢ R&D (Copy dán TikTok/Facebook...):", 
                 value=st.session_state['analysis_report'], 
                 key=f"text_area_{st.session_state['text_key']}")
