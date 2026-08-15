import streamlit as st
from PIL import Image
from google import genai
from google.genai import types
import gc
import re
import datetime

# ---------------------------------------------------------
# 1. CẤU HÌNH GIAO DIỆN MỆNH KIM PREMIUM (HIỆU ỨNG 3D TABS)
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

    /* NÚT BẤM CHÍNH 3D */
    .stButton > button { 
        width: 100%; height: 55px; font-size: 19px; font-weight: 900; 
        background: linear-gradient(135deg, #FFDF00 0%, #D4AF37 100%) !important; 
        color: #121418 !important; border: 1px solid #FFF34D !important; border-radius: 10px !important;
        box-shadow: 0 6px 15px rgba(212, 175, 55, 0.4), inset 0px 2px 5px rgba(255,255,255,0.6) !important;
        transition: all 0.2s ease;
    }
    .stButton > button:active { transform: translateY(3px); box-shadow: 0 2px 5px rgba(212, 175, 55, 0.4) !important; }

    /* THIẾT KẾ 3D CHO TABS */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; padding-bottom: 5px; }
    
    /* Tab chưa chọn - Hiệu ứng phím cơ chìm */
    .stTabs [data-baseweb="tab"] { 
        background: linear-gradient(145deg, #2D333F, #21262F) !important; 
        border: 1px solid #3A4150 !important; border-bottom: none !important; 
        border-radius: 12px 12px 0px 0px !important; padding: 12px 18px !important; color: #9CA3AF !important;
        box-shadow: 3px -3px 8px rgba(0,0,0,0.4), inset 1px 1px 2px rgba(255,255,255,0.05) !important;
        transition: all 0.2s ease-in-out;
    }
    .stTabs [data-baseweb="tab"]:hover { transform: translateY(-2px); color: #E0E6ED !important; }

    /* Tab đang chọn - Hiệu ứng vàng khối nhô cao 3D */
    .stTabs [aria-selected="true"] { 
        background: linear-gradient(145deg, #FFDF00, #D4AF37) !important; 
        color: #121418 !important; font-weight: 900 !important; 
        border: 1px solid #FFF585 !important; border-bottom: none !important;
        transform: translateY(-5px); 
        box-shadow: 0px -8px 15px rgba(212, 175, 55, 0.4), inset 2px 2px 5px rgba(255,255,255,0.5), inset -2px -2px 5px rgba(0,0,0,0.15) !important;
        z-index: 10;
    }
    
    /* KHUNG CARD HIỂN THỊ NỘI DUNG */
    .vip-card { 
        background-color: #252A34 !important; border: 2px solid #FFD700 !important; 
        border-radius: 0px 12px 12px 12px; padding: 25px; 
        box-shadow: inset 0px 5px 15px rgba(0,0,0,0.5), 0 10px 25px rgba(0,0,0,0.4);
    }
    .vip-text { font-family: 'Consolas', monospace; font-size: 15px; line-height: 1.6; white-space: pre-wrap; color: #F3F4F6 !important; }
    .vip-footer { 
        text-align: center; border-top: 1px dashed #FFD700; padding-top: 15px; 
        margin-top: 20px; color: #9CA3AF; font-size: 12px; 
        display: flex; justify-content: space-between; align-items: center;
    }
    
    /* Highlight Cảnh báo */
    .warning-box { border-left: 4px solid #FF3B30; background-color: rgba(255,59,48,0.1); padding: 10px 15px; border-radius: 5px; }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)
st.markdown("<h1 class='title-brand'>DN SIM MY LEAGUE</h1>", unsafe_allow_html=True)
st.markdown("<p class='slogan'>Giải Mã Sơ Đồ - Định Hình Meta - Kiến Tạo Dream Team</p>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. KHỐI NHẬP LIỆU (ĐÃ MỞ KHÓA MULTI-UPLOAD)
# ---------------------------------------------------------
player_info = st.text_input("Tên Cầu thủ/Sơ đồ (Bỏ trống nếu không cần):", placeholder="Ví dụ: Mason Mount hoặc 4-2-1-3")
ecosystem = st.selectbox("Chọn hệ sinh thái (SIM AI / PvP):", ["SIM AI", "PvP"])
is_comparison = st.checkbox("✅ ĐÂY LÀ ẢNH SO SÁNH CẦU THỦ (Trái: AUTO | Phải: MANUAL DNS)")

st.markdown("<p style='color: #FFD700; font-weight: bold; margin-bottom: 0px;'>📸 1. Tải ảnh Cầu thủ (CÓ THỂ QUÉT CHỌN NHIỀU ẢNH CÙNG LÚC):</p>", unsafe_allow_html=True)
uploaded_players = st.file_uploader("Kéo thả: Ảnh eFHUB + Ảnh In-game Dual Styles", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True, key="player_imgs")

st.markdown("<p style='color: #FFD700; font-weight: bold; margin-bottom: 0px;'>📸 2. Tải ảnh HLV (Kéo thả ảnh HLV vào đây):</p>", unsafe_allow_html=True)
uploaded_managers = st.file_uploader("Kéo thả ảnh Manager", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True, key="manager_imgs")

# ---------------------------------------------------------
# 3. BỘ NÃO AI LOGIC VIP (KÈM CÔNG TẮC "KILL SWITCH" AN TOÀN)
# ---------------------------------------------------------
def clean_text(raw_text):
    text = raw_text.replace("$", "").replace("#", "")
    text = text.replace("\\rightarrow", "->").replace("\\Rightarrow", "=>")
    # Đổi chữ in đậm sang HTML
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    text = text.replace("> ", "🔹 ")
    # Bôi đỏ khối cảnh báo nếu AI tạo ra
    if "🚨" in text or "CẢNH BÁO" in text:
        text = text.replace("🚨", "<div class='warning-box'>🚨")
        text = text.replace("Vui lòng upload bổ sung ảnh in-game nhé!", "Vui lòng upload bổ sung ảnh in-game nhé!</div>")
    return text

def execute_tactical_analysis(img_list, p_info, eco, is_comp):
    try:
        api_key = st.secrets.get("GEMINI_API_KEY")
        if not api_key: return "[LỖI CẤU HÌNH]: Không tìm thấy GEMINI_API_KEY!"
            
        client = genai.Client(api_key=api_key)
        
        system_instruction = """
        Bạn là DNS TACTICAL ARCHITECT - Chuyên gia Phân tích Chiến thuật eFootball VIP.

        🛑 [QUY TẮC KILL SWITCH - BẮT BUỘC ĐỌC ĐẦU TIÊN]: 
        Hãy quét TẤT CẢ các ảnh được cung cấp để tìm thông tin "Dual Styles" (Trạng thái Đỏ / Xanh của cầu thủ in-game). 
        - NẾU KHÔNG TÌM THẤY: Bạn TUYỆT ĐỐI TỪ CHỐI xuất báo cáo. Chỉ in ra đúng dòng này: "🚨 **CẢNH BÁO TỬ HUYỆT:** Không tìm thấy dữ liệu Dual Styles Đỏ/Xanh in-game. Để tránh rủi ro Build sai PP làm gãy hệ thống Fluid Formation, Bot đình chỉ phân tích. Boss vui lòng upload bổ sung ảnh in-game nhé!" và DỪNG HOÀN TOÀN (Không xuất dấu === hay Phần 2,3,4).
        - NẾU TÌM THẤY HOẶC ĐÂY CHỈ LÀ ẢNH HLV: Tiếp tục phân tích theo cấu trúc 4 Phần bên dưới.

        QUY TẮC ĐỊNH DẠNG:
        - BẮT BUỘC CHIA VĂN BẢN THÀNH 4 PHẦN CHÍNH. Ngăn cách giữa các phần bằng CHÍNH XÁC 3 dấu bằng: "===" (Mỗi cụm === nằm riêng trên 1 dòng).

        PHẦN 1: HỒ SƠ THẨM ĐỊNH & SA BÀN (Trước === thứ nhất)
        🔹 Thẩm định phôi & Phân tích Dual Styles (Trạng thái Đỏ/Xanh).
        🔹 TƯ DUY FLUID FORMATION: Bóc tách Sơ đồ Công / Sơ đồ Thủ. Từ đó Đề xuất Style HLV (LBC/QC/Poss...) để không đứt gãy cự ly.

        ===
        PHẦN 2: NÂNG CẤP CHỈ SỐ PP (Giữa === 1 và 2)
        🔹 LUẬT TÍNH PP LŨY TIẾN CỨNG: 1-4 nấc tốn 1PP/nấc; 5-8 nấc tốn 2PP/nấc; 9-12 nấc tốn 3PP/nấc; 13-16 nấc tốn 4PP/nấc.
        🔹 Phân bổ nấc nâng song ngữ: Speed (Tốc độ), Stamina (Thể lực)... 
        👉 TỔNG KẾT TIÊU HAO: Cộng dồn tổng PP tiêu tốn chuẩn xác so với tổng quỹ điểm. Đề xuất 1 Booster Slot 2.

        ===
        PHẦN 3: SO SÁNH AUTO vs DNS MANUAL (Giữa === 2 và 3)
        🔹 CỘT TRÁI là Auto. CỘT PHẢI là DNS Manual. So sánh Delta (+/-) theo chuẩn: "Speed (Tốc độ): Auto 103 👉 DNS 101 (-2)".
        🔹 ĐỌC MANAGER BOOSTS: CHỈ lấy chữ Vàng/Cam dưới tên HLV. Không lấy icon lục giác cầu thủ. Đọc Link-up Tactic.
        🏆 TỔNG KẾT: Chỉ ra điểm mù bản Auto và ưu thế DNS Manual.

        ===
        PHẦN 4: CÀI ĐẶT & KỸ NĂNG (Sau === thứ 3)
        🎯 INDIVIDUAL INSTRUCTIONS: Max 2 Tấn công, Max 2 Phòng ngự.
        🧩 TOP 5 SKILL BỔ SUNG: Dùng cờ 1️⃣ đến 5️⃣.
        🎙️ INSIGHT CHUYÊN MÔN.
        """
        config = types.GenerateContentConfig(system_instruction=system_instruction, temperature=0.1)
        
        comp_text = "ĐÂY LÀ ẢNH SO SÁNH. (TRÁI LÀ AUTO, PHẢI LÀ DNS MANUAL)." if is_comp else ""
        context_prompt = f"Thông tin/Sơ đồ: {p_info} | Chế độ: {eco}. {comp_text}"
        
        contents = [context_prompt] + img_list
            
        response = client.models.generate_content(model='gemini-3.6-flash', contents=contents, config=config)
        return clean_text(response.text)
    except Exception as e:
        if "503" in str(e): return "[MÁY CHỦ BẬN]: Hệ thống Gemini quá tải tạm thời."
        return f"[LỖI HỆ THỐNG]: {str(e)}"

# ---------------------------------------------------------
# 4. XỬ LÝ SỰ KIỆN & IN PHIẾU VIP 
# ---------------------------------------------------------
if st.button("BẮT ĐẦU PHÂN TÍCH VIP"):
    if not uploaded_players and not uploaded_managers: 
        st.error("Vui lòng tải ít nhất 1 ảnh Cầu thủ HOẶC 1 ảnh HLV!")
    else:
        with st.spinner("Hệ thống DNS đang trích xuất Báo cáo VIP..."):
            images_to_send = []
            
            if uploaded_players:
                for f in uploaded_players:
                    img = Image.open(f); img.thumbnail((1000, 1000))
                    images_to_send.append(img)
            if uploaded_managers:
                for f in uploaded_managers:
                    img = Image.open(f); img.thumbnail((1000, 1000))
                    images_to_send.append(img)
                
            st.session_state['analysis_report'] = execute_tactical_analysis(images_to_send, player_info, ecosystem, is_comparison)
            
            # Ghi nhận thời gian thực
            vn_time = datetime.datetime.utcnow() + datetime.timedelta(hours=7)
            st.session_state['report_time'] = vn_time.strftime("%d/%m/%Y | %H:%M:%S")
            
            images_to_send.clear()
            gc.collect()

if 'analysis_report' in st.session_state:
    parts = st.session_state['analysis_report'].split("===")
    
    # Kịch bản nếu AI kích hoạt Kill Switch (Từ chối xuất vì thiếu ảnh)
    if len(parts) == 1 and "🚨" in parts[0]:
        tab1_c = parts[0]
        tab2_c = "⚠️ *Hệ thống đình chỉ tính toán PP do thiếu dữ liệu in-game.*"
        tab3_c = "⚠️ *Hệ thống đình chỉ so sánh do rủi ro sai lệch dữ liệu.*"
        tab4_c = "⚠️ *Hệ thống đình chỉ tư vấn cài đặt cá nhân.*"
    else:
        tab1_c = parts[0] if len(parts) > 0 else "Đang xử lý..."
        tab2_c = parts[1] if len(parts) > 1 else "Không có dữ liệu PP."
        tab3_c = parts[2] if len(parts) > 2 else "Không có dữ liệu So sánh."
        tab4_c = parts[3] if len(parts) > 3 else "Không có dữ liệu Cài đặt."
    
    report_time = st.session_state.get('report_time', 'Chưa xác định')
    
    # KHỞI TẠO 4 TAB 3D MỚI
    t1, t2, t3, t4 = st.tabs(["🪪 HỒ SƠ THẨM ĐỊNH", "🛠️ NÂNG CẤP CHỈ SỐ", "⚖️ SO SÁNH ĐỐI ĐẦU", "🎯 CÀI ĐẶT KỸ NĂNG"])
    
    def format_tab(content):
        return f"""<div class="vip-card">
            <div style="text-align:center; margin-bottom: 15px;"><img src="https://i.postimg.cc/4KNSdqRd/D9754823-56B4-4957-8F90-1EE072CFF5A2.jpg" style="max-width: 90px; border-radius: 8px;"></div>
            <div class="vip-text">{content.strip()}</div>
            <div class="vip-footer">
                <span style="color: #9CA3AF; font-style: italic;">Đồng bộ lúc: {report_time}</span>
                <span style="color: #FFD700; font-weight: bold; font-size: 13px;">© 2026 DN SIM MY LEAGUE</span>
            </div>
        </div>"""

    with t1: st.markdown(format_tab(tab1_c), unsafe_allow_html=True)
    with t2: st.markdown(format_tab(tab2_c), unsafe_allow_html=True)
    with t3: st.markdown(format_tab(tab3_c), unsafe_allow_html=True)
    with t4: st.markdown(format_tab(tab4_c), unsafe_allow_html=True)
    
    with st.expander("Bấm vào đây để Copy văn bản thô (Dành cho Team Content)"):
        # Dọn sạch thẻ HTML để copy dán sạch sẽ nhất
        raw_text_clean = st.session_state['analysis_report'].replace("<b>", "").replace("</b>", "").replace("<div class='warning-box'>", "").replace("</div>", "").replace("===", "\n\n")
        st.text_area("Văn bản gốc:", value=raw_text_clean, height=200)
