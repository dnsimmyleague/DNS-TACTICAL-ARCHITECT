import streamlit as st
from PIL import Image
from google import genai
from google.genai import types
import gc
import re
import datetime

# ---------------------------------------------------------
# 1. HỆ THỐNG GIAO DIỆN MỆNH KIM: TỰ ĐỘNG THEO THỜI GIAN THỰC (SÁNG/TỐI)
# ---------------------------------------------------------
st.set_page_config(page_title="DN SIM MY LEAGUE | VIP DNS", page_icon="👑", layout="centered")

# Lấy giờ thực tế tại Việt Nam (UTC+7) để tự động đổi Theme Sáng/Tối
current_hour = (datetime.datetime.utcnow() + datetime.timedelta(hours=7)).hour
is_daytime = 6 <= current_hour < 18

if is_daytime:
    # GIAO DIỆN BAN NGÀY (LIGHT LUXURY GOLD)
    theme_bg = "#F4F6F9"
    card_bg = "#FFFFFF"
    text_color = "#111827"
    tab_inactive_bg = "linear-gradient(145deg, #E5E7EB, #D1D5DB)"
    tab_inactive_color = "#4B5563"
    border_color = "#D4AF37"
    mode_badge = "☀️ GIAO DIỆN: BAN NGÀY"
else:
    # GIAO DIỆN BAN ĐÊM (DARK KNIGHT GOLD)
    theme_bg = "#1E222A"
    card_bg = "#252A34"
    text_color = "#F3F4F6"
    tab_inactive_bg = "linear-gradient(145deg, #2D333F, #21262F)"
    tab_inactive_color = "#9CA3AF"
    border_color = "#FFD700"
    mode_badge = "🌙 GIAO DIỆN: BAN ĐÊM"

custom_css = f"""
<style>
    #MainMenu {{visibility: hidden;}} footer {{visibility: hidden;}} header {{visibility: hidden;}}
    .stApp {{ background-color: {theme_bg} !important; }}
    
    .title-brand {{ 
        text-align: center; color: #FFD700 !important; font-size: 2.4rem; 
        font-weight: 900; margin-bottom: 5px; letter-spacing: 2px;
        text-shadow: 0px 2px 10px rgba(255, 215, 0, 0.3);
    }}
    .slogan {{ text-align: center; color: {text_color} !important; font-size: 1.05rem; font-style: italic; margin-bottom: 25px; }}

    .stTextInput > div > div > input, .stSelectbox > div > div > div {{
        background-color: #FFFFFF !important; color: #111827 !important;
        font-weight: 600 !important; border-radius: 8px !important; border: 1px solid #D4AF37 !important;
    }}
    label, .stCheckbox > label > div > p {{ color: #FFD700 !important; font-weight: bold !important; font-size: 15px !important;}}

    .stButton > button {{ 
        width: 100%; height: 55px; font-size: 19px; font-weight: 900; 
        background: linear-gradient(135deg, #FFDF00 0%, #D4AF37 100%) !important; 
        color: #121418 !important; border: 1px solid #FFF34D !important; border-radius: 10px !important;
        box-shadow: 0 6px 15px rgba(212, 175, 55, 0.4), inset 0px 2px 5px rgba(255,255,255,0.6) !important;
    }}

    .stTabs [data-baseweb="tab-list"] {{ gap: 10px; padding-bottom: 5px; }}
    
    .stTabs [data-baseweb="tab"] {{ 
        background: {tab_inactive_bg} !important; 
        border: 1px solid {border_color} !important; border-bottom: none !important; 
        border-radius: 12px 12px 0px 0px !important; padding: 12px 18px !important; color: {tab_inactive_color} !important;
        box-shadow: 3px -3px 8px rgba(0,0,0,0.2) !important;
    }}

    .stTabs [aria-selected="true"] {{ 
        background: linear-gradient(145deg, #FFDF00, #D4AF37) !important; 
        color: #121418 !important; font-weight: 900 !important; 
        border: 1px solid #FFF585 !important; border-bottom: none !important;
        transform: translateY(-5px); 
        box-shadow: 0px -8px 15px rgba(212, 175, 55, 0.4) !important;
    }}
    
    .vip-card {{ 
        background-color: {card_bg} !important; border: 2px solid {border_color} !important; 
        border-radius: 0px 12px 12px 12px; padding: 25px; 
        box-shadow: 0 10px 25px rgba(0,0,0,0.2);
    }}
    .vip-text {{ font-family: 'Consolas', monospace; font-size: 15px; line-height: 1.6; white-space: pre-wrap; color: {text_color} !important; }}
    .vip-footer {{ 
        text-align: center; border-top: 1px dashed {border_color}; padding-top: 15px; 
        margin-top: 20px; color: #9CA3AF; font-size: 13px; 
        display: flex; justify-content: space-between; align-items: center;
    }}
    .warning-box {{ border-left: 4px solid #FF3B30; background-color: rgba(255,59,48,0.15); padding: 12px 15px; border-radius: 6px; margin-bottom: 10px; color: #FF3B30 !important; font-weight: bold; }}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)
st.markdown("<h1 class='title-brand'>DN SIM MY LEAGUE</h1>", unsafe_allow_html=True)
st.markdown(f"<p class='slogan'>Giải Mã Sơ Đồ - Định Hình Meta - Kiến Tạo Dream Team ({mode_badge})</p>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. KHỐI NHẬP LIỆU (QUÉT NHIỀU ẢNH)
# ---------------------------------------------------------
player_info = st.text_input("Tên Cầu thủ/Sơ đồ (Bỏ trống nếu không cần):", placeholder="Ví dụ: Roberto Carlos hoặc 4-2-1-3")
ecosystem = st.selectbox("Chọn hệ sinh thái (SIM AI / PvP):", ["SIM AI", "PvP"])
is_comparison = st.checkbox("✅ ĐÂY LÀ ẢNH SO SÁNH CẦU THỦ (Trái: AUTO | Phải: MANUAL DNS)")

st.markdown("<p style='color: #FFD700; font-weight: bold; margin-bottom: 0px;'>📸 1. Tải ảnh Cầu thủ (eFHUB và Ảnh Dual Styles in-game):</p>", unsafe_allow_html=True)
uploaded_players = st.file_uploader("Có thể quét chọn nhiều ảnh cùng lúc", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True, key="player_imgs")

st.markdown("<p style='color: #FFD700; font-weight: bold; margin-bottom: 0px;'>📸 2. Tải ảnh HLV (Link-up / Manager Buff):</p>", unsafe_allow_html=True)
uploaded_managers = st.file_uploader("Có thể quét chọn nhiều ảnh HLV", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True, key="manager_imgs")

# ---------------------------------------------------------
# 3. LÕI TƯ DUY AI (BỘ NÃO)
# ---------------------------------------------------------
def clean_text(raw_text):
    text = raw_text.replace("$", "").replace("#", "")
    text = text.replace("\\rightarrow", "->").replace("\\Rightarrow", "=>")
    # Biến Markdown in đậm thành thẻ HTML <b>
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    text = text.replace("> ", "🔹 ")
    # Bọc đỏ khung cảnh báo
    if "🚨" in text or "CẢNH BÁO TỬ HUYỆT" in text:
        text = f"<div class='warning-box'>{text}</div>"
    return text

def execute_tactical_analysis(img_list, p_info, eco, is_comp):
    try:
        api_key = st.secrets.get("GEMINI_API_KEY")
        if not api_key: return "[LỖI CẤU HÌNH]: Không tìm thấy GEMINI_API_KEY!"
            
        client = genai.Client(api_key=api_key)
        
        system_instruction = """
        Bạn là DNS TACTICAL ARCHITECT.
        
        🛑 QUY TẮC KILL SWITCH (KIỂM DUYỆT ĐẦU VÀO):
        - Quét tất cả ảnh. Nếu có ảnh Cầu thủ nhưng KHÔNG THẤY ảnh màn hình in-game hiển thị Playing Style Đỏ và Xanh (Dual Styles), BẠN PHẢI TỪ CHỐI PHÂN TÍCH.
        - Chỉ in ra đúng 1 câu duy nhất: "🚨 CẢNH BÁO TỬ HUYỆT: Không phát hiện ảnh in-game hiển thị Dual Styles (Đỏ/Xanh). Để tránh rủi ro Build sai điểm PP làm gãy cự ly Fluid Formation, Bot đình chỉ phân tích. Boss vui lòng upload bổ sung ảnh in-game nhé!". (Không xuất các phần khác).
        - Nếu ĐÃ CÓ đủ ảnh Dual Styles (hoặc đây chỉ là ảnh HLV), thì tiếp tục phân tích 4 Phần bên dưới.
        
        ĐỊNH DẠNG ĐẦU RA: Chia thành đúng 4 phần ngăn cách bởi "===" (trên 1 dòng riêng).
        
        PHẦN 1: HỒ SƠ THẨM ĐỊNH & SA BÀN (Trước === thứ 1)
        - Thẩm định phôi & Phân tích Dual Styles (Đỏ/Xanh).
        - Fluid Formation: Bóc tách sơ đồ Công / Thủ. Đề xuất Style HLV bắt buộc (LBC/QC/Poss...).
        
        ===
        PHẦN 2: NÂNG CẤP CHỈ SỐ PP (Giữa === 1 và 2)
        - Luật PP lũy tiến: 1-4=1PP, 5-8=2PP, 9-12=3PP, 13-16=4PP.
        - Phân bổ nấc nâng song ngữ. Tính tổng tiêu hao PP không được dư.
        - 1 Booster Slot 2 đề xuất.
        
        ===
        PHẦN 3: SO SÁNH AUTO vs DNS MANUAL (Giữa === 2 và 3)
        - ĐỊNH DẠNG BẮT BUỘC ĐỂ SO SÁNH (Lấy Cột Phải làm chuẩn tính Delta +/-): 
          Ví dụ: Speed (Tốc độ): Auto 103 👉 DNS 101 (-2)
        - ĐỌC HLV: Chỉ lấy chữ màu Vàng/Cam dưới tên HLV làm Manager Boosts. Đọc Link-up Tactic.
        
        ===
        PHẦN 4: CÀI ĐẶT & KỸ NĂNG (Sau === thứ 3)
        - Individual Instructions (Max 2 slot Tấn Công, Max 2 slot Phòng Ngự).
        - Top 5 Skill bổ sung ưu tiên (Dùng số thứ tự 1️⃣ đến 5️⃣).
        - Insight chốt hạ dành cho Streamer.
        """
        config = types.GenerateContentConfig(system_instruction=system_instruction, temperature=0.1)
        
        comp_text = "ĐÂY LÀ ẢNH SO SÁNH (TRÁI: AUTO, PHẢI: DNS MANUAL)." if is_comp else ""
        context_prompt = f"Thông tin: {p_info} | Hệ: {eco}. {comp_text}"
        
        contents = [context_prompt] + img_list
        response = client.models.generate_content(model='gemini-3.6-flash', contents=contents, config=config)
        return clean_text(response.text)
    except Exception as e:
        return f"[LỖI HỆ THỐNG]: {str(e)}"

# ---------------------------------------------------------
# 4. TRÍCH XUẤT VÀ HIỂN THỊ
# ---------------------------------------------------------
if st.button("BẮT ĐẦU PHÂN TÍCH VIP"):
    if not uploaded_players and not uploaded_managers: 
        st.error("Vui lòng tải ít nhất 1 ảnh Cầu thủ hoặc HLV!")
    else:
        with st.spinner("Đang trích xuất Báo cáo Sa bàn..."):
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
    if len(parts) == 1 and ("🚨" in parts[0] or "CẢNH BÁO" in parts[0]):
        tab1_c = parts[0]
        tab2_c = "<div class='warning-box'>⚠️ Hệ thống đình chỉ tính toán PP do thiếu dữ liệu in-game.</div>"
        tab3_c = "<div class='warning-box'>⚠️ Hệ thống đình chỉ so sánh do rủi ro sai lệch dữ liệu.</div>"
        tab4_c = "<div class='warning-box'>⚠️ Hệ thống đình chỉ tư vấn cài đặt cá nhân.</div>"
    else:
        tab1_c = parts[0] if len(parts) > 0 else "Đang xử lý..."
        tab2_c = parts[1] if len(parts) > 1 else "Không có dữ liệu PP."
        tab3_c = parts[2] if len(parts) > 2 else "Không có dữ liệu So sánh."
        tab4_c = parts[3] if len(parts) > 3 else "Không có dữ liệu Cài đặt."
    
    report_time = st.session_state.get('report_time', 'Chưa xác định')
    
    t1, t2, t3, t4 = st.tabs(["🪪 HỒ SƠ THẨM ĐỊNH", "🛠️ NÂNG CẤP CHỈ SỐ", "⚖️ SO SÁNH ĐỐI ĐẦU", "🎯 CÀI ĐẶT KỸ NĂNG"])
    
    def format_tab(content):
        return f"""<div class="vip-card">
            <div style="text-align:center; margin-bottom: 15px;"><img src="https://i.postimg.cc/4KNSdqRd/D9754823-56B4-4957-8F90-1EE072CFF5A2.jpg" style="max-width: 90px; border-radius: 8px;"></div>
            <div class="vip-text">{content.strip()}</div>
            <div class="vip-footer">
                <span style="color: #9CA3AF; font-style: italic;">Đồng bộ lúc: {report_time}</span>
                <span style="color: #FFD700; font-weight: bold;">© 2026 DN SIM MY LEAGUE</span>
            </div>
        </div>"""

    with t1: st.markdown(format_tab(tab1_c), unsafe_allow_html=True)
    with t2: st.markdown(format_tab(tab2_c), unsafe_allow_html=True)
    with t3: st.markdown(format_tab(tab3_c), unsafe_allow_html=True)
    with t4: st.markdown(format_tab(tab4_c), unsafe_allow_html=True)
    
    with st.expander("Bấm vào đây để Copy văn bản thô (Dành cho Team Content)"):
        # Dọn sạch các thẻ HTML để Copy/Paste sạch sẽ
        raw_text_clean = st.session_state['analysis_report'].replace("<b>", "").replace("</b>", "").replace("<div class='warning-box'>", "").replace("</div>", "").replace("===", "\n\n")
        st.text_area("Văn bản gốc:", value=raw_text_clean, height=200)
