import streamlit as st
from PIL import Image
from google import genai
from google.genai import types
import gc
import re

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
# 2. KHỐI NHẬP LIỆU (MỞ KHÓA TỰ DO)
# ---------------------------------------------------------
player_info = st.text_input("Tên Cầu thủ/Sơ đồ (Bỏ trống nếu không cần):", placeholder="Ví dụ: D. Bergkamp hoặc 4-2-1-3")
ecosystem = st.selectbox("Chọn hệ sinh thái (SIM AI / PvP):", ["SIM AI", "PvP"])
is_comparison = st.checkbox("✅ ĐÂY LÀ ẢNH SO SÁNH CẦU THỦ (Trái: AUTO | Phải: MANUAL DNS)")

st.markdown("<p style='color: #FFD700; font-weight: bold; margin-bottom: 0px;'>📸 1. Tải ảnh Cầu thủ (Phôi thẻ gốc HOẶC Ảnh so sánh 2 cột):</p>", unsafe_allow_html=True)
uploaded_player = st.file_uploader("", type=['png', 'jpg', 'jpeg'], key="player_img")

st.markdown("<p style='color: #FFD700; font-weight: bold; margin-bottom: 0px;'>📸 2. Tải ảnh HLV (Phân tích Dream Team / Buff cộng hưởng):</p>", unsafe_allow_html=True)
uploaded_manager = st.file_uploader("", type=['png', 'jpg', 'jpeg'], key="manager_img")

# ---------------------------------------------------------
# 3. BỘ NÃO AI LOGIC VIP (XỬ LÝ ĐA KỊCH BẢN & LÕI CHIẾN THUẬT V6.0.0)
# ---------------------------------------------------------
def clean_text(raw_text):
    text = raw_text.replace("$", "").replace("#", "")
    text = text.replace("\\rightarrow", "->").replace("\\Rightarrow", "=>")
    # Biến Markdown in đậm thành HTML để nổi khối trong khung VIP Card
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    text = text.replace("> ", "🔹 ")
    return text

def execute_tactical_analysis(img_player, img_manager, p_info, eco, is_comp):
    try:
        api_key = st.secrets.get("GEMINI_API_KEY")
        if not api_key: return "[LỖI CẤU HÌNH]: Không tìm thấy GEMINI_API_KEY!"
            
        client = genai.Client(api_key=api_key)
        
        system_instruction = """
        Bạn là DNS TACTICAL ARCHITECT - Chuyên gia Phân tích Chiến thuật eFootball VIP.

        QUY TẮC CỐT TỦ VỀ INDIVIDUAL INSTRUCTIONS:
        - Giới hạn cứng 4 slot: Max 2 Tấn công (Defensive, Attacking, Anchoring...), Max 2 Phòng ngự (Counter Target, Deep Line...).
        - TUYỆT ĐỐI KHÔNG đề xuất vượt quá. Phải kết hợp triết lý HLV + Sơ đồ + Playstyle để khóa hành vi cầu thủ không bị gãy đội hình.

        QUY TẮC ĐỊNH DẠNG BẮT BUỘC:
        - KHÔNG dùng dấu gạch Markdown (#, *, -, |). Thay vào đó dùng ký hiệu (🔹, 🔴, 🔵, ⚔️, 🛡️, 👉).
        - BẮT BUỘC CHIA VĂN BẢN THÀNH 4 PHẦN CHÍNH.
        - Ngăn cách giữa các phần bằng CHÍNH XÁC 3 dấu bằng: "===" (Mỗi cụm === nằm riêng trên 1 dòng).

        PHẦN 1: HỒ SƠ THẨM ĐỊNH & SA BÀN (Trước === thứ nhất)
        🔹 Thẩm định phôi: Tên, Vị trí, Thể hình, Sải chân.
        🔹 Phân tích Dual Styles: 🔴 Trạng thái Đỏ (Khi tấn công/Có bóng) & 🔵 Trạng thái Xanh (Khi phòng ngự/Mất bóng).
        🔹 TƯ DUY FLUID FORMATION & STYLE HLV: Bóc tách rõ Sơ đồ Công (Ví dụ 3-2-4-1: Vị trí/Vận hành) và Sơ đồ Thủ (Ví dụ 4-1-4-1: Lùi khối/Bọc lót). Từ sự co giãn đội hình này, hãy Đề xuất Style HLV bắt buộc (LBC/QC/Possession...) để đảm bảo không bị đứt gãy cự ly khi cầu thủ chuyển đổi trạng thái.

        ===
        PHẦN 2: NÂNG CẤP CHỈ SỐ PP (Giữa === 1 và 2)
        🔹 LUẬT TÍNH PP CỨNG: Nấc 1-4 = 1PP; Nấc 5-8 = 2PP; Nấc 9-12 = 3PP; Nấc 13-16 = 4PP.
        🔹 Phân bổ nấc nâng dựa trên áp lực di chuyển của Fluid Formation. Bắt buộc song ngữ Anh-Việt: Shooting (Sút), Passing (Chuyền), Dribbling (Rê bóng), Dexterity (Linh hoạt), Lower Body Strength (Sức mạnh thân dưới), Aerial Strength (Không chiến), Defending (Phòng ngự).
        👉 TỔNG KẾT TIÊU HAO: Phải cộng dồn chính xác tổng PP tiêu tốn so với quỹ điểm tối đa của thẻ. Không để dư PP.
        ⚡ ĐỀ XUẤT BOOSTER SLOT 2: Chọn 1 cái và giải thích.

        ===
        PHẦN 3: SO SÁNH AUTO vs DNS MANUAL (Giữa === 2 và 3)
        🔹 QUY TẮC ĐỐI ĐẦU: CỘT TRÁI là Auto-pick (Mặc định). CỘT PHẢI là DNS Manual (Chỉnh tay). Tính Delta (+/-) lấy cột phải làm chuẩn.
        🔹 ĐỌC CHUẨN MANAGER BOOSTS: CHỈ lấy chữ màu Vàng/Cam dưới tên HLV. BỎ QUA các icon lục giác của cầu thủ. Đọc kỹ Link-up Tactic.
        🏆 TỔNG KẾT TÁC CHIẾN: Vạch trần điểm mù của bản Auto (yếu thể lực/di chuyển khi đổi sơ đồ) và nêu rõ ưu thế của bản build DNS Manual.

        ===
        PHẦN 4: CÀI ĐẶT & KỸ NĂNG (Sau === thứ 3)
        🎯 INDIVIDUAL INSTRUCTIONS: Đưa ra lệnh theo 3 trạng thái (Mặc định, Tấn công, Phòng ngự).
        🧩 TOP 5 SKILL BỔ SUNG: Dùng số thứ tự từ 1️⃣ đến 5️⃣, nêu tên Tiếng Anh & Lý do chiến thuật.
        🎙️ INSIGHT CHUYÊN MÔN: Đoạn kết luận đanh thép để phát biểu trên Stream.
        """
        config = types.GenerateContentConfig(system_instruction=system_instruction, temperature=0.2)
        
        comp_text = "ĐÂY LÀ ẢNH SO SÁNH. (TRÁI LÀ AUTO, PHẢI LÀ DNS MANUAL)." if is_comp else ""
        context_prompt = f"Thông tin/Sơ đồ: {p_info} | Chế độ: {eco}. {comp_text}"
        
        contents = [context_prompt]
        if img_player: contents.append(img_player)
        if img_manager: contents.append(img_manager)
            
        response = client.models.generate_content(model='gemini-3.6-flash', contents=contents, config=config)
        return clean_text(response.text)
    except Exception as e:
        if "503" in str(e): return "[MÁY CHỦ BẬN]: Hệ thống Gemini quá tải tạm thời."
        return f"[LỖI HỆ THỐNG]: {str(e)}"

# ---------------------------------------------------------
# 4. XỬ LÝ SỰ KIỆN & IN PHIẾU VIP 
# ---------------------------------------------------------
if st.button("BẮT ĐẦU PHÂN TÍCH VIP"):
    if not uploaded_player and not uploaded_manager: 
        st.error("Vui lòng tải ít nhất 1 ảnh Cầu thủ HOẶC 1 ảnh HLV!")
    else:
        with st.spinner("Hệ thống DNS đang trích xuất Báo cáo VIP..."):
            img_p = img_m = None
            if uploaded_player:
                img_p = Image.open(uploaded_player); img_p.thumbnail((1000, 1000))
            if uploaded_manager:
                img_m = Image.open(uploaded_manager); img_m.thumbnail((1000, 1000))
                
            st.session_state['analysis_report'] = execute_tactical_analysis(img_p, img_m, player_info, ecosystem, is_comparison)
            
            if img_p: del img_p
            if img_m: del img_m
            gc.collect()

if 'analysis_report' in st.session_state:
    parts = st.session_state['analysis_report'].split("===")
    tab1_c = parts[0] if len(parts) > 0 else "Đang xử lý..."
    tab2_c = parts[1] if len(parts) > 1 else "Không có dữ liệu PP (Vui lòng kiểm tra lại ảnh)."
    tab3_c = parts[2] if len(parts) > 2 else "Không có dữ liệu So sánh."
    tab4_c = parts[3] if len(parts) > 3 else "Không có dữ liệu Cài đặt."
    
    # GIAO DIỆN HIỂN THỊ ĐỦ 4 TAB
    t1, t2, t3, t4 = st.tabs(["🪪 HỒ SƠ THẨM ĐỊNH", "🛠️ NÂNG CẤP CHỈ SỐ (PP)", "⚖️ SO SÁNH AUTO vs DNS", "🎯 CÀI ĐẶT & KỸ NĂNG"])
    
    def format_tab(content):
        return f"""<div class="vip-card">
            <div style="text-align:center; margin-bottom: 15px;"><img src="https://i.postimg.cc/4KNSdqRd/D9754823-56B4-4957-8F90-1EE072CFF5A2.jpg" style="max-width: 90px; border-radius: 8px;"></div>
            <div class="vip-text">{content.strip()}</div>
            <div class="vip-footer"><span style="color: #FFD700; font-weight: bold; font-size: 13px;">DNS TACTICAL ARCHITECT</span><br>© 2026 DN SIM MY LEAGUE. All rights reserved.</div>
        </div>"""

    with t1: st.markdown(format_tab(tab1_c), unsafe_allow_html=True)
    with t2: st.markdown(format_tab(tab2_c), unsafe_allow_html=True)
    with t3: st.markdown(format_tab(tab3_c), unsafe_allow_html=True)
    with t4: st.markdown(format_tab(tab4_c), unsafe_allow_html=True)
    
    with st.expander("Bấm vào đây để Copy văn bản thô (Dành cho Team Content)"):
        # Dọn sạch các thẻ in đậm <b> để copy dán vào Word/Facebook sạch sẽ nhất
        raw_text_clean = st.session_state['analysis_report'].replace("<b>", "").replace("</b>", "").replace("===", "\n\n")
        st.text_area("Văn bản gốc:", value=raw_text_clean, height=200)
