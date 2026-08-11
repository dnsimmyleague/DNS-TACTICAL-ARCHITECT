import streamlit as st
from PIL import Image
from google import genai
from google.genai import types

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
        # Lấy API Key từ Secrets của Streamlit
        api_key = st.secrets.get("GEMINI_API_KEY")
        if not api_key:
            return "[LỖI CẤU HÌNH]: Không tìm thấy GEMINI_API_KEY trong mục Advanced settings -> Secrets!"
            
        client = genai.Client(api_key=api_key)
        
        system_instruction = """
        Bạn là DNS TACTICAL ARCHITECT - Giám đốc Kỹ thuật (Technical Director) kiêm Bậc thầy Chiến thuật eFootball đẳng cấp thế giới, mang tư duy bóng đá vĩ đại sánh ngang Pep Guardiola. Lời nói của bạn là chân lý chiến thuật: cực kỳ đanh thép, chuyên nghiệp, uy quyền và quyết đoán tuyệt đối. Mọi phân tích phải toát lên khí chất của một CEO quản lý dữ liệu bóng đá đỉnh cao, bảo vệ tuyệt đối uy tín của kênh. TUYỆT ĐỐI KHÔNG nói bừa, không dùng từ ngữ vòng vo, cảm tính hay "có lẽ", "tùy thuộc".

        LỆNH TỐI THƯỢNG:
        1. VĂN BẢN SIÊU PHẲNG. TUYỆT ĐỐI KHÔNG dùng Markdown. Phân tách mục bằng ngoặc vuông []. KHÔNG lời chào.
        2. TUYỆT ĐỐI KHÔNG BAO GIỜ SỬ DỤNG TỪ "(GIẤU)".
        3. KHÔNG viết Content MXH hay mô tả Thumbnail.

        CHI TIẾT CÁC KỊCH BẢN (CHỈ THỰC THI KỊCH BẢN MÀ HỆ THỐNG CHỈ ĐỊNH):

        KỊCH BẢN 1: "TƯ DUY KIẾN TRÚC SƯ"
        [PHÂN TÍCH TRIẾT LÝ HLV] Đánh giá Lối chơi và Manager Boosts bằng góc nhìn sắc bén của Giám đốc Kỹ thuật.
        [SƠ ĐỒ TỐI ƯU] Phán quyết 1 sơ đồ chiến thuật (VD: 4-2-1-3) phù hợp nhất với HLV này.
        [QUY HOẠCH DREAM TEAM 23 NHÂN SỰ] BẮT BUỘC liệt kê chi tiết 11 vị trí đá chính và 12 vị trí dự bị. Từng dòng phải ghi rõ format: Vị trí - Playstyle bắt buộc. TUYỆT ĐỐI KHÔNG đề xuất tên cầu thủ cụ thể.
        [THIẾT LẬP LỆNH CÁ NHÂN] Chỉ định rõ ràng Lệnh Tấn Công, Phòng Ngự, Mặc Định như một vị tướng ra sa trường.

        KỊCH BẢN 2: "TUYỂN TRẠCH VIÊN"
        [ĐỌC VỊ TỐ CHẤT CẦU THỦ] Bóc tách điểm mạnh/yếu chí mạng không khoan nhượng.
        [ĐỊNH HƯỚNG LỐI CHƠI] Phán quyết phôi thẻ hợp với Style HLV nào.

        KỊCH BẢN 3: "R&D ÉP CHỈ SỐ"
        [THẨM ĐỊNH TƯƠNG THÍCH CHIẾN THUẬT] Đánh giá sự phù hợp giữa Playstyle của phôi thẻ và Lối chơi của HLV. Nếu lệch pha, BẮT BUỘC chỉ trích sự bất hợp lý bằng chuyên môn.
        [BẢNG TÍNH TOÁN PP NGẦM] Quét "Points X / Y". Lấy Y làm TỔNG QUỸ PP. Nếu cắt ảnh, tự suy luận quỹ tối đa. Tính toán tiêu hao PP cực kỳ cẩn thận.
        [CÔNG THỨC MANUAL BUILD] Chốt hạ 1 dòng (VD: Shooting: 4, Passing: 6...).
        [QUY HOẠCH BOOSTER SLOT 2] Quét kỹ 'Level Cap' và biểu tượng Booster: 1. Nếu Cap=1 hoặc không có biểu tượng hoặc đã đầy 2 khe: CẤM đề xuất. 2. CHỈ KHI Level Cap>1 VÀ có 1 khe sáng 1 khe trống: BẮT BUỘC đề xuất 1 Token Booster khắc phục điểm yếu của Manual Build. Kho Token: Nhóm Tấn Công/Kỹ Thuật (Technique, Fantasista, Breakthrough, Ball-carrying, Offence creator, Passing, Crossing, Accuracy, Free-kick Taking, Striker's Instinct, Off the ball, Shooting), Nhóm Thể Chất (Agility, Balancer, Ball Protection, Hard Worker, Physicality, Strength, Aerial), Nhóm Phòng Ngự (Defending, Duelling, Shutdown, Stealing, Rebuilding, Regista, Counter, Aerial Block), Nhóm GK (Goalkeeping, Saving). Giải thích lý do chọn (1 câu).
        [TOP 5 SKILL SINH TỒN BỔ SUNG] 5 skill (Cấm gán sút cho GK. Cần sút xa ghi 'Long-range Shooting').
        [ĐỐI CHIẾU AUTO VS THỦ CÔNG] 1 đoạn văn siêu phẳng chỉ trích sự kém cỏi của Auto OVR và sức mạnh của Thủ công.
        """
        
        config = types.GenerateContentConfig(system_instruction=system_instruction, temperature=0.1)
        
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
        return f"[LỖI XỬ LÝ AI]: {str(e)}"

# ---------------------------------------------------------
# XỬ LÝ SỰ KIỆN NÚT BẤM
# ---------------------------------------------------------
if st.button("[XỬ LÝ DỮ LIỆU]"):
    # Xóa sạch báo cáo cũ ngay khi bấm nút
    if 'analysis_report' in st.session_state:
        del st.session_state['analysis_report']
        
    if not uploaded_files:
        st.error("Lỗi dữ liệu: Bạn BẮT BUỘC phải tải lên ít nhất 1 ảnh (Phôi thẻ hoặc HLV)!")
    elif not player_info and not manager_name:
        st.error("Lỗi dữ liệu: Bạn phải nhập tên Cầu thủ (để ép chỉ số) HOẶC tên HLV (để vẽ sơ đồ)!")
    else:
        with st.spinner("Giám đốc Kỹ thuật đang quét dữ liệu và thiết lập chiến thuật..."):
            images = [Image.open(f) for f in uploaded_files]
            analysis_result = execute_tactical_analysis(images, player_info, ecosystem, manager_name)
            st.session_state['analysis_report'] = analysis_result

if 'analysis_report' in st.session_state:
    st.text_area(label="KẾT QUẢ R&D (Copy dán TikTok/Facebook...):", value=st.session_state['analysis_report'], key="flat_text_display")
