import streamlit as st
from PIL import Image
from google import genai
from google.genai import types
from google.genai.errors import APIError
import gc
import re
import datetime
import json
import time

# ---------------------------------------------------------
# 1. CẤU HÌNH TRANG & GIAO DIỆN NỀN TẢNG (DNS ARCHITECT)
# ---------------------------------------------------------
st.set_page_config(page_title="DN SIM MY LEAGUE | DNS", page_icon="⚽", layout="centered")

vn_time_now = datetime.datetime.utcnow() + datetime.timedelta(hours=7)
default_is_daytime = 6 <= vn_time_now.hour < 18

if 'manual_theme' not in st.session_state:
    st.session_state['manual_theme'] = "☀️" if default_is_daytime else "🌙"

if 'project_tray' not in st.session_state:
    st.session_state['project_tray'] = []

selected_theme = st.radio("Theme Switcher", ["☀️", "🌙"], 
                          index=0 if st.session_state['manual_theme'] == "☀️" else 1,
                          horizontal=True, label_visibility="collapsed")
st.session_state['manual_theme'] = selected_theme
is_daytime = (st.session_state['manual_theme'] == "☀️")

logo_url = "https://i.postimg.cc/ydpJLXP9/26529F2E-29C2-40BD-B202-BEDC09BAE6F9.png"

if is_daytime:
    app_bg = "#F4F6F9"; element_bg = "#FFFFFF"; text_color = "#1E293B"
    label_color = "#D4AF37"; slogan_color = "#64748B"; border_color = "#D4AF37"
    shadow_3d = "6px 6px 14px rgba(0,0,0,0.06), -6px -6px 14px rgba(255,255,255,0.9)"
    tab_inactive_bg = "#E2E8F0"; tab_inactive_color = "#0F172A"  
    expander_copy_bg = "#F8FAFC"
    subtab_bg = "linear-gradient(145deg, #f0f0f0, #cacaca)"
    subtab_shadow = "5px 5px 12px #bebebe, -5px -5px 12px #ffffff"
    subtab_active_bg = "linear-gradient(145deg, #D4AF37, #B8860B)"
    subtab_active_shadow = "inset 5px 5px 10px #9a7009, inset -5px -5px 10px #fceea5"
else:
    app_bg = "#1E222A"; element_bg = "#252A34"; text_color = "#F1F5F9"
    label_color = "#E5C058"; slogan_color = "#94A3B8"; border_color = "#D4AF37"
    shadow_3d = "6px 6px 14px rgba(0,0,0,0.35), -4px -4px 10px rgba(255,255,255,0.03)"
    tab_inactive_bg = "#1E222A"; tab_inactive_color = "#FFFFFF"  
    expander_copy_bg = "#1A1D24"
    subtab_bg = "linear-gradient(145deg, #21252e, #1c1f26)"
    subtab_shadow = "5px 5px 12px #15181d, -5px -5px 12px #2d323f"
    subtab_active_bg = "linear-gradient(145deg, #E5C058, #C89B2B)"
    subtab_active_shadow = "inset 5px 5px 10px #a68124, inset -5px -5px 10px #ffdf30"

custom_css = f"""
<style>
    header[data-testid="stHeader"] {{ display: none !important; }} footer {{ display: none !important; }}
    .stApp {{ background-color: {app_bg} !important; transition: background-color 0.4s ease; }}
    div[data-testid="stSpinner"] {{ background-color: transparent !important; }}
    div[data-testid="stSpinner"] svg circle {{ stroke: {border_color} !important; }}
    div[data-testid="stSpinner"] > div > span, div[data-testid="stSpinner"] p {{ color: {label_color} !important; font-weight: 900 !important; font-size: 17px !important; text-shadow: 1px 1px 3px rgba(0,0,0,0.5); }}
    
    .stApp::before {{ 
        content: ""; position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); 
        width: 85vw; max-width: 450px; height: 85vw; max-height: 450px; 
        background-image: url('{logo_url}'); background-size: contain; background-repeat: no-repeat; 
        background-position: center; opacity: 0.15; pointer-events: none; z-index: 999999; 
    }}
    
    [data-testid="stAppViewBlockContainer"] {{ position: relative; z-index: 10; padding-top: 3rem !important; }}
    
    div[data-testid="stRadio"] {{ 
        position: fixed !important; top: 12px !important; right: 12px !important; z-index: 999999 !important; 
        background-color: {element_bg} !important; border: 1.5px solid {border_color} !important; 
        border-radius: 30px !important; padding: 2px 10px !important; box-shadow: {shadow_3d} !important; 
        opacity: 0.65; transition: opacity 0.3s ease, transform 0.3s ease; 
    }}
    div[data-testid="stRadio"]:hover, div[data-testid="stRadio"]:active {{ opacity: 1; transform: scale(1.05); }}
    div[data-testid="stRadio"] label p {{ font-size: 18px !important; margin: 0 !important; padding: 0 !important; }}
    
    .title-brand {{ text-align: center; color: {border_color} !important; font-size: 2.5rem; font-weight: 900; margin-bottom: 5px; letter-spacing: 2px; text-shadow: 0px 4px 12px rgba(212, 175, 55, 0.35); }}
    .slogan {{ text-align: center; color: {slogan_color} !important; font-size: 1.05rem; font-style: italic; margin-bottom: 25px; }}
    label {{ color: {label_color} !important; font-weight: bold !important; font-size: 15px !important; }}
    .stTextInput>div>div>input, .stSelectbox>div>div>div {{ background-color: {element_bg} !important; color: {text_color} !important; font-weight: 600 !important; border-radius: 12px !important; border: 1px solid {border_color} !important; box-shadow: {shadow_3d} !important; }}
    [data-testid="stFileUploader"] section {{ background-color: {element_bg} !important; border: 1.5px dashed {border_color} !important; border-radius: 15px !important; box-shadow: {shadow_3d} !important; }}
    [data-testid="stFileUploader"] button {{ background: linear-gradient(135deg, #E5C058, #B8860B) !important; color: #121418 !important; font-weight: bold !important; }}
    .stButton > button {{ width: 100%; height: 58px; font-size: 19px; font-weight: 900; background: linear-gradient(135deg, #E5C058, #B8860B) !important; color: #121418 !important; border-radius: 12px !important; box-shadow: 0 8px 18px rgba(184, 134, 11, 0.35); }}
    
    div[data-testid="stTabs"] button[data-baseweb="tab"] {{ background-color: {tab_inactive_bg} !important; border: 2px solid rgba(212, 175, 55, 0.6) !important; border-bottom: none !important; border-radius: 14px 14px 0px 0px !important; padding: 12px 18px !important; }}
    div[data-testid="stTabs"] button[data-baseweb="tab"] p {{ color: {tab_inactive_color} !important; font-weight: 800 !important; }}
    div[data-testid="stTabs"] button[aria-selected="true"] {{ background: linear-gradient(145deg, #E5C058, #C89B2B) !important; transform: translateY(-6px); box-shadow: 0px -6px 15px rgba(200, 155, 43, 0.4) !important; }}
    div[data-testid="stTabs"] button[aria-selected="true"] p {{ color: #121418 !important; font-weight: 900 !important; }}
    div[data-testid="stTabs"] div[data-testid="stTabs"] button[data-baseweb="tab"] {{ background: {subtab_bg} !important; border-radius: 12px !important; transform: none; box-shadow: {subtab_shadow} !important; }}
    div[data-testid="stTabs"] div[data-testid="stTabs"] button[aria-selected="true"] {{ background: {subtab_active_bg} !important; border: 1.5px solid {border_color} !important; box-shadow: {subtab_active_shadow} !important; }}
    
    .dns-card {{ background-color: {element_bg} !important; border: 2px solid {border_color} !important; border-radius: 0px 15px 15px 15px; padding: 25px; box-shadow: {shadow_3d} !important; position: relative; z-index: 2; margin-bottom: 20px; }}
    .dns-text {{ font-family: 'Consolas', monospace; font-size: 15px; line-height: 1.7; color: {text_color} !important; }}
    .dns-footer {{ text-align: center; border-top: 1px dashed {border_color}; padding-top: 15px; margin-top: 25px; font-size: 13px; display: flex; justify-content: space-between; align-items: center; }}
    .warning-box {{ border-left: 5px solid #FF4D4D; background-color: rgba(255,77,77,0.15); padding: 12px 15px; border-radius: 8px; color: #FF4D4D !important; font-weight: bold; margin-bottom: 12px; }}
    
    .dns-expander summary {{ padding: 15px; font-weight: 800; color: {label_color}; background: {subtab_bg}; cursor: pointer; border-radius: 10px; border: 1px solid rgba(212, 175, 55, 0.3); list-style: none; transition: all 0.2s; box-shadow: 3px 3px 8px rgba(0,0,0,0.2); margin-bottom: 10px; }}
    .dns-expander[open] summary {{ border-bottom: 1px dashed {border_color}; background: {subtab_active_bg}; color: #121418 !important; box-shadow: {subtab_active_shadow}; margin-bottom: 0px; border-radius: 10px 10px 0 0; }}
    .dns-expander summary::-webkit-details-marker {{ display: none; }}
    .expander-content {{ padding: 15px; background: {app_bg}; color: {text_color} !important; font-size: 14.5px; border-top: 1px solid rgba(212, 175, 55, 0.1); border-left: 1px solid rgba(212, 175, 55, 0.3); border-right: 1px solid rgba(212, 175, 55, 0.3); border-bottom: 1px solid rgba(212, 175, 55, 0.3); border-radius: 0 0 10px 10px; margin-bottom: 15px; box-shadow: 3px 3px 8px rgba(0,0,0,0.1); }}
    
    .tray-box {{ background-color: {element_bg}; border: 1.5px dashed {border_color}; border-radius: 12px; padding: 15px; margin-top: 25px; box-shadow: {shadow_3d}; }}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)
st.markdown("<h1 class='title-brand'>DN SIM MY LEAGUE</h1>", unsafe_allow_html=True)
st.markdown("<p class='slogan'>Giải Mã Sơ Đồ - Định Hình Meta - Kiến Tạo Dream Team</p>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. KHỐI NHẬP LIỆU
# ---------------------------------------------------------
analysis_mode = st.selectbox(
    "🎯 CHỌN CHẾ ĐỘ PHÂN TÍCH:",
    [
        "1. Khám Phôi Thẻ Auto Mặc định (Có sao xài vậy, Hợp/Loại)",
        "2. Thẩm Định & Build PP (Thẻ có Level)",
        "3. Khám HLV Tổng Quan (Chỉ phân tích Sơ đồ & Triết lý)",
        "4. Build Dream Team 23 Người (Dựa trên HLV)",
        "5. Dự án Video: So Sánh Auto vs Manual DNS"
    ]
)

col1, col2 = st.columns(2)
with col1:
    player_info = st.text_input("👤 Tên Cầu thủ/Sơ đồ:", placeholder="Ví dụ: Roberto Carlos, 4-2-1-3...")
    ecosystem = st.selectbox("🌐 Chọn hệ sinh thái (SIM AI / PvP):", ["SIM AI", "PvP"], index=1)
    is_compare = st.checkbox("🔍 Kích hoạt So sánh (Dành cho 2 ảnh trở lên)", value=False)
with col2:
    uploaded_players = st.file_uploader("📸 1. Tải ảnh Cầu thủ (eFHUB/In-game):", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)
    uploaded_managers = st.file_uploader("📸 2. Tải ảnh HLV (Manager Buff):", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)

# ---------------------------------------------------------
# 3. HÀM KẾT XUẤT JSON VÀ UI (LÕI BỌC THÉP V8.0)
# ---------------------------------------------------------
def render_expander_from_json(items):
    if not items or len(items) == 0: 
        return "<p style='color: #64748B; font-style: italic; text-align: center; padding: 20px;'>Chưa có dữ liệu phân bổ.</p>"
    html_out = ""
    for item in items:
        title = item.get("vitri", "Vị trí")
        loai = item.get("loai", "Đá chính")
        style = item.get("style", "")
        vaitro = item.get("vaitro", "")
        content = f"<strong>Phân loại:</strong> {loai}<br><strong>Style đề xuất:</strong> <span style='color:{label_color}; font-weight:800;'>{style}</span><br><strong>Vai trò:</strong> {vaitro}"
        html_out += f'<details class="dns-expander"><summary>{title} ({loai})</summary><div class="expander-content"><p>🔹 {content}</p></div></details>'
    return html_out

def format_in_game_json(data):
    if not data: return ""
    inst = data.get("individual_instructions", {})
    
    html_out = "<strong>1. Cài đặt Lệnh Cá nhân (Bám sát Sơ đồ Kép Công/Thủ):</strong><br><br>"
    
    html_out += f"🔹 <strong style='color:#FF4D4D;'>Tấn công (In Possession - Tối đa 4 Slot):</strong><br>"
    for key in ["AT1", "AT2", "AT3", "AT4"]:
        if key in inst and inst[key].get("lenh"):
            html_out += f"<span style='margin-left: 20px;'>🔸 {key}: <strong>{inst[key].get('lenh')}</strong> cho {inst[key].get('vitri')}</span><br>"
    
    html_out += f"<br>🔹 <strong style='color:#4D94FF;'>Phòng ngự (Out Possession - Tối đa 4 Slot):</strong><br>"
    for key in ["DF1", "DF2", "DF3", "DF4"]:
        if key in inst and inst[key].get("lenh"):
            html_out += f"<span style='margin-left: 20px;'>🔸 {key}: <strong>{inst[key].get('lenh')}</strong> cho {inst[key].get('vitri')}</span><br>"
    
    html_out += "<br><strong>2. Kịch bản Thay người (Mental Level):</strong><br><br>"
    html_out += f"🔹 <strong>Start Game:</strong> {data.get('k1', '')}<br>"
    html_out += f"🔹 <strong>Đang dẫn bàn (Nấc Xanh):</strong> {data.get('k2', '')}<br>"
    html_out += f"🔹 <strong>Bị dẫn bàn (Nấc Đỏ):</strong> {data.get('k3', '')}"
    
    top_skills = data.get("top_5_skills", [])
    if top_skills and isinstance(top_skills, list):
        html_out += "<br><br><strong>3. Top 5 Skills Bắt Buộc (Chỉ gán nếu phôi thẻ chưa có):</strong><br><br>"
        for skill in top_skills:
            html_out += f"⭐ {skill}<br>"
            
    return html_out

def extract_json_safe(text):
    try:
        match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL | re.IGNORECASE)
        if match:
            try: return json.loads(match.group(1))
            except: pass
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1 and end > start:
            try: return json.loads(text[start:end+1])
            except: pass
    except: pass
    return None

def translate_json_to_markdown(json_23, json_ingame):
    md_out = "=== QUY HOẠCH 23 CẦU THỦ ===\n\n"
    if json_23:
        for tuyen in ["FW", "MF", "DF", "GK"]:
            if tuyen in json_23:
                md_out += f"--- Tuyến {tuyen} ---\n"
                for item in json_23[tuyen]:
                    md_out += f"- {item.get('vitri', '')} ({item.get('loai', '')}): Style {item.get('style', '')}. Vai trò: {item.get('vaitro', '')}\n"
    
    if json_ingame:
        md_out += "\n=== CÀI ĐẶT LỆNH 4 SLOT IN-GAME ===\n\n"
        inst = json_ingame.get("individual_instructions", {})
        for k in ["AT1", "AT2", "AT3", "AT4", "DF1", "DF2", "DF3", "DF4"]:
            if k in inst and inst[k].get("lenh"):
                md_out += f"🔸 {k}: {inst[k].get('lenh')} cho {inst[k].get('vitri')}\n"
            
        md_out += f"\n🔸 Kịch bản thay người:\n   - Start Game: {json_ingame.get('k1', '')}\n   - Dẫn bàn (Xanh): {json_ingame.get('k2', '')}\n   - Bị dẫn (Đỏ): {json_ingame.get('k3', '')}\n"
        
        skills = json_ingame.get("top_5_skills", [])
        if skills:
            md_out += "\n🔸 Top 5 Skills Bắt Buộc:\n"
            for s in skills: md_out += f"   - {s}\n"
            
    return md_out

# ---------------------------------------------------------
# 4. LÕI TƯ DUY AI (V8.0 - KHÓA TỬ HUYỆT CẤU TRÚC JSON)
# ---------------------------------------------------------
def execute_tactical_analysis(img_list, p_info, eco, mode, is_compare_mode):
    try:
        api_key = st.secrets.get("GEMINI_API_KEY")
        if not api_key: return "[LỖI CẤU HÌNH]: Không tìm thấy GEMINI_API_KEY!"
        client = genai.Client(api_key=api_key)
        
        hard_rules = """
        [ĐÓNG VAI TRÒ: CHUYÊN GIA PHÂN TÍCH CHIẾN THUẬT THỰC CHIẾN]
        [LUẬT THÉP eFOOTBALL 2027 KHẮT KHE - NẾU VI PHẠM SẼ BỊ HỦY LỆNH]:
        1. QUY TẮC NGÔN NGỮ: Dùng từ chuyên môn thực chiến, lập luận ĐA CHIỀU. TUYỆT ĐỐI KHÔNG ghi "chưa tính buff HLV". Đọc chuẩn số xanh lá. Tuyệt đối không dùng từ R&D.
        2. QUY TẮC SKILL (CỰC KỲ QUAN TRỌNG): 
           - CẤM đề xuất Kỹ năng đặc biệt không thể học (Phenomenal Finishing, Blitz Curler, Momentum Dribbling, Visionary Pass, Edged Crossing, Fortress). CHỈ đề xuất Kỹ năng có thể gán.
           - Phải soi kỹ ảnh Cầu thủ, TUYỆT ĐỐI KHÔNG đề xuất lại Skill mà cầu thủ đã có sẵn.
        3. LUẬT LỆNH CÁ NHÂN: Konami ĐÃ XÓA "Deep Line". CẤM DÙNG TỪ NÀY. Phân bổ lệnh vào 4 slot Tấn Công (AT1->AT4) và 4 slot Phòng Ngự (DF1->DF4).
        4. LUẬT CẤU TRÚC (SỐNG CÒN): Phải xuất chính xác 3 dấu === để chia làm 4 phần.
        """

        if "1" in mode:
            tab1_cmd = "Đánh giá Phôi Auto 5 chiều. Cân nhắc Dual Playstyle. KẾT LUẬN: Hợp/Loại."
            tab2_cmd = "CẢNH BÁO TỪ CHỐI."
            tab3_cmd = "CẢNH BÁO TỪ CHỐI."
            tab4_cmd = "Lệnh cá nhân In-game & 3 kịch bản tâm lý."
            
        elif "2" in mode:
            tab1_cmd = "Đánh giá sự tương thích sơ đồ. Đề xuất Slot Booster (Crafting +1)."
            tab2_cmd = "BẮT BUỘC liệt kê RÕ CÔNG THỨC PHÂN BỔ ĐIỂM (Ví dụ: Shooting: 8, Dexterity: 12...). SAU ĐÓ BẮT BUỘC viết lập luận phân tích CHI TIẾT lý do cộng điểm. NẾU CÓ Style Xanh đặc biệt, giải thích cách trích quỹ PP nuôi thể lực/phòng ngự."
            tab3_cmd = "CẢNH BÁO TỪ CHỐI."
            tab4_cmd = "Đề xuất Lệnh Cá Nhân phù hợp (AT1/AT2/DF1/DF2) và Top 5 Skills (TUÂN THỦ TUYỆT ĐỐI QUY TẮC CẤM ĐỀ XUẤT LẠI SKILL ĐÃ CÓ VÀ SKILL KHÔNG THỂ HỌC)."
            
        elif "3" in mode:
            tab1_cmd = "Khám HLV Tổng Quan: 1. Triết lý. 2. Đề xuất Sơ đồ luân phiên (Công & Thủ). 3. TACTICAL LINKS. (Tuyệt đối dừng lại ở HLV, không build Dream Team 23 người ở đây)."
            tab2_cmd = "CẢNH BÁO TỪ CHỐI."
            tab3_cmd = "CẢNH BÁO TỪ CHỐI."
            tab4_cmd = "Cài đặt Lệnh Cá Nhân. BẮT BUỘC đề xuất các slot lệnh AT (Tối đa 4) và DF (Tối đa 4) bám sát Sơ đồ Kép. CẤM DÙNG DEEP LINE. Viết dạng văn xuôi giải thích chi tiết, không xuất JSON."
            
        elif "4" in mode:
            # DỒN TOÀN BỘ VĂN XUÔI LÊN TAB 1 ĐỂ BẢO VỆ TAB 2, TAB 4
            tab1_cmd = "1. Phân tích Triết lý HLV, Sơ đồ luân phiên. 2. Giải mã TACTICAL LINKS. 3. Giải thích lý do lựa chọn 23 cầu thủ và lý do cài đặt các lệnh In-game. TẤT CẢ VĂN XUÔI PHẢI NẰM Ở ĐÂY."
            tab2_cmd = """[KỶ LUẬT THÉP CỰC ĐỘ]: BẮT BUỘC CHỈ TRẢ VỀ 1 KHỐI JSON DUY NHẤT. TUYỆT ĐỐI KHÔNG VIẾT VĂN XUÔI Ở PHẦN NÀY. KHÔNG DÙNG TÊN CẦU THỦ NGOÀI ĐỜI.
            ```json
            {
              "FW": [{"vitri": "CF", "loai": "Đá chính", "style": "Goal Poacher", "vaitro": "Mũi khoan"}],
              "MF": [{"vitri": "DMF", "loai": "Đá chính", "style": "Anchor Man", "vaitro": "Mỏ neo"}],
              "DF": [{"vitri": "CB", "loai": "Đá chính", "style": "Build Up", "vaitro": "Phát động"}],
              "GK": [{"vitri": "GK", "loai": "Đá chính", "style": "Offensive GK", "vaitro": "Băng ra"}]
            }
            ```"""
            tab3_cmd = "CẢNH BÁO TỪ CHỐI."
            tab4_cmd = """[KỶ LUẬT THÉP CỰC ĐỘ]: BẮT BUỘC CHỈ TRẢ VỀ 1 KHỐI JSON DUY NHẤT. TUYỆT ĐỐI KHÔNG VIẾT VĂN XUÔI. CẤM SỬ DỤNG "DEEP LINE". KHÔNG ĐỀ XUẤT SKILLS Ở CHẾ ĐỘ LÊN KHUNG NÀY.
            ```json
            {
              "individual_instructions": {
                "AT1": {"lenh": "Anchoring", "vitri": "LWF"},
                "AT2": {"lenh": "Offensive", "vitri": "CB"},
                "DF1": {"lenh": "Counter Target", "vitri": "CF"},
                "DF2": {"lenh": "Tight Marking", "vitri": "AMF"}
              },
              "k1": "Xuất phát...", "k2": "Phòng ngự...", "k3": "Tấn công..."
            }
            ```"""
        elif "5" in mode:
            tab1_cmd = "SO SÁNH TỔNG QUAN: So sánh sự khác biệt về tư duy lối chơi, đánh giá điểm yếu của thẻ Auto."
            tab2_cmd = "PHÂN TÍCH CHÊNH LỆCH PP: Đi sâu vào chênh lệch các chỉ số Tiếng Anh (Speed, Awareness...). Giải thích tại sao cách Build DNS (Thủ công) lại mang tính sát thương cao hơn."
            tab3_cmd = "CẢNH BÁO TỪ CHỐI."
            tab4_cmd = "KỊCH BẢN VIDEO & THUMBNAIL: Đề xuất 3 tiêu đề giật gân, câu view và 1 kịch bản ngắn gọn gọn gàng để làm video Tiktok/Shorts so sánh."
        else:
            tab1_cmd = "CẢNH BÁO TỪ CHỐI."; tab2_cmd = "CẢNH BÁO TỪ CHỐI."; tab3_cmd = "CẢNH BÁO TỪ CHỐI."; tab4_cmd = "CẢNH BÁO TỪ CHỐI."

        system_instruction = f"""
        {hard_rules}
        BẠN BẮT BUỘC PHẢI CHIA BÁO CÁO THÀNH ĐÚNG 4 PHẦN, NGĂN CÁCH NHAU BỞI CHÍNH XÁC 3 DẤU BẰNG "===" NẰM ĐỘC LẬP TRÊN 1 DÒNG. KHÔNG ĐƯỢC THIẾU HAY DƯ DẤU "===".
        
        {tab1_cmd}
        ===
        {tab2_cmd}
        ===
        {tab3_cmd}
        ===
        {tab4_cmd}
        """
        
        context_prompt = f"Thông tin: {p_info} | Hệ: {eco} | Chế độ: {mode}"
        if is_compare_mode: context_prompt += " | YÊU CẦU ĐẶC BIỆT: Thực hiện so sánh chi tiết giữa các ảnh được cung cấp."
            
        config = types.GenerateContentConfig(system_instruction=system_instruction, temperature=0.1)
        contents = [context_prompt] + img_list
        
        client_models = ['gemini-3.6-flash']
        last_error = ""
        
        for attempt in range(3): 
            for m in client_models:
                try:
                    response = client.models.generate_content(model=m, contents=contents, config=config)
                    if response and response.text: return response.text
                except Exception as api_err: 
                    last_error = str(api_err)
                    if "503" in last_error or "429" in last_error:
                        time.sleep(3) 
                        continue
                    else:
                        break 
            if "503" not in last_error and "429" not in last_error: break
            
        return f"[LỖI TỪ GOOGLE API]: {last_error}"
    except Exception as e: return f"[LỖI HỆ THỐNG]: {str(e)}"

# ---------------------------------------------------------
# 5. RENDER BÁO CÁO KẾT QUẢ & LƯU KHAY DỰ ÁN
# ---------------------------------------------------------
if st.button("🚀 BẮT ĐẦU PHÂN TÍCH"):
    if not uploaded_players and not uploaded_managers: 
        st.error("Vui lòng tải ít nhất 1 ảnh Cầu thủ hoặc HLV!")
    else:
        with st.spinner("Đang trích xuất Báo cáo Sa bàn..."):
            images_to_send = []
            if uploaded_players: 
                for f in uploaded_players: images_to_send.append(Image.open(f).copy())
            if uploaded_managers: 
                for f in uploaded_managers: images_to_send.append(Image.open(f).copy())
                    
            st.session_state['raw_report'] = execute_tactical_analysis(images_to_send, player_info, ecosystem, analysis_mode, is_compare)
            st.session_state['report_time'] = vn_time_now.strftime("%d/%m/%Y | %H:%M:%S")

if 'raw_report' in st.session_state:
    mode_selected = analysis_mode[0]
    raw_text = st.session_state['raw_report'].replace("⛔ ", "").replace("*", "")
    parts = raw_text.split("===")
    
    tab1_c = parts[0].strip() if len(parts) > 0 else ""
    tab2_c = parts[1].strip() if len(parts) > 1 else ""
    tab3_c = parts[2].strip() if len(parts) > 2 else ""
    tab4_c = parts[3].strip() if len(parts) > 3 else ""
    
    report_time = st.session_state.get('report_time', vn_time_now.strftime("%d/%m/%Y | %H:%M:%S"))
    footer_text_color = "#64748B" if is_daytime else "#94A3B8"
    
    def format_tab_content(content):
        if "CẢNH BÁO TỪ CHỐI" in content and len(content) < 150:
            return f"<div class='warning-box'>⛔ Tính năng này đã bị khóa do không thuộc phạm vi của Chế độ phân tích hiện tại.</div>"
        html_content = content.replace('\n', '<br>')
        return f"""<div class="dns-card">
            <div class="dns-text">{html_content}</div>
            <div class="dns-footer">
                <span style="color: {footer_text_color}; font-style: italic; font-weight: 600;">Đồng bộ lúc: {report_time}</span>
                <span style="color: {label_color}; font-weight: 900;">© 2027 DN SIM MY LEAGUE. All rights reserved.</span>
            </div>
        </div>"""

    if mode_selected == "4":
        t1, t2, t4 = st.tabs(["🪪 THẨM ĐỊNH & TRIẾT LÝ", "🛠️ QUY HOẠCH 23 CẦU THỦ", "🎯 CÀI ĐẶT LỆNH IN-GAME"])
        with t1: st.markdown(format_tab_content(tab1_c), unsafe_allow_html=True)
        
        json_data_23 = extract_json_safe(tab2_c)
        json_data_ingame = extract_json_safe(tab4_c)
        
        with t2: 
            if json_data_23 and any(k in json_data_23 for k in ["FW", "MF", "DF", "GK"]):
                s1, s2, s3, s4 = st.tabs(["⚽ FW", "🎯 MF", "🛡️ DF", "🧤 GK"])
                with s1: st.markdown(render_expander_from_json(json_data_23.get("FW", [])), unsafe_allow_html=True)
                with s2: st.markdown(render_expander_from_json(json_data_23.get("MF", [])), unsafe_allow_html=True)
                with s3: st.markdown(render_expander_from_json(json_data_23.get("DF", [])), unsafe_allow_html=True)
                with s4: st.markdown(render_expander_from_json(json_data_23.get("GK", [])), unsafe_allow_html=True)
            else:
                st.markdown(format_tab_content(f"<span style='color:#FF4D4D;font-weight:bold;'>⚠️ AI xuất dữ liệu sai định dạng JSON. Dưới đây là bản thô:</span><br><br>{tab2_c}"), unsafe_allow_html=True)
                
        with t4: 
            if json_data_ingame and "individual_instructions" in json_data_ingame: 
                st.markdown(format_tab_content(format_in_game_json(json_data_ingame)), unsafe_allow_html=True)
            else: 
                st.markdown(format_tab_content(f"<span style='color:#FF4D4D;font-weight:bold;'>⚠️ AI xuất dữ liệu sai định dạng JSON. Dưới đây là bản thô:</span><br><br>{tab4_c}"), unsafe_allow_html=True)
            
        raw_to_save = f"{tab1_c}\n\n{translate_json_to_markdown(json_data_23, json_data_ingame)}"

    elif mode_selected == "5":
        t1, t2, t4 = st.tabs(["⚖️ SO SÁNH TỔNG QUAN", "🛠️ PHÂN TÍCH CHÊNH LỆCH PP", "🎬 KỊCH BẢN THUMBNAIL"])
        with t1: st.markdown(format_tab_content(tab1_c), unsafe_allow_html=True)
        with t2: st.markdown(format_tab_content(tab2_c), unsafe_allow_html=True)
        with t4: st.markdown(format_tab_content(tab4_c), unsafe_allow_html=True)
        raw_to_save = f"{tab1_c}\n\n{tab2_c}\n\n{tab4_c}"

    elif mode_selected == "3":
        t1, t4 = st.tabs(["🪪 TRIẾT LÝ & SƠ ĐỒ KÉP", "🎯 LỆNH CÁ NHÂN (4 SLOT)"])
        with t1: st.markdown(format_tab_content(tab1_c), unsafe_allow_html=True)
        with t4: st.markdown(format_tab_content(tab4_c), unsafe_allow_html=True)
        raw_to_save = f"{tab1_c}\n\n{tab4_c}"

    elif mode_selected == "2":
        t1, t2, t4 = st.tabs(["🪪 THẨM ĐỊNH & BOOSTER", "🛠️ BẢNG BUILD PP", "🎯 LỆNH IN-GAME & TOP 5 SKILLS"])
        with t1: st.markdown(format_tab_content(tab1_c), unsafe_allow_html=True)
        with t2: st.markdown(format_tab_content(tab2_c), unsafe_allow_html=True)
        with t4: st.markdown(format_tab_content(tab4_c), unsafe_allow_html=True)
        raw_to_save = f"{tab1_c}\n\n{tab2_c}\n\n{tab4_c}"

    else:
        t1, t2, t4 = st.tabs(["🪪 THẨM ĐỊNH & TRIẾT LÝ", "🛠️ PHÂN BỔ PP", "🎯 CÀI ĐẶT LỆNH & SKILLS"])
        with t1: st.markdown(format_tab_content(tab1_c), unsafe_allow_html=True)
        with t2: st.markdown(format_tab_content(tab2_c), unsafe_allow_html=True)
        with t4: st.markdown(format_tab_content(tab4_c), unsafe_allow_html=True)
        raw_to_save = raw_text.replace("===", "\n\n")
        
    st.markdown("---")
    col_save, col_dl = st.columns(2)
    with col_save:
        if st.button("💾 LƯU BÁO CÁO NÀY VÀO KHAY"):
            current_title = player_info if player_info else f"Báo cáo lúc {report_time}"
            st.session_state['project_tray'].append({
                "title": current_title,
                "content": raw_to_save.strip()
            })
            st.rerun()

    if len(st.session_state['project_tray']) > 0:
        master_text = "=== HỒ SƠ THẨM ĐỊNH CHIẾN THUẬT - DN SIM MY LEAGUE ===\n\n"
        for idx, item in enumerate(st.session_state['project_tray']):
            master_text += f"--- {idx + 1}. {item['title']} ---\n{item['content']}\n\n"
            
        with col_dl:
            st.download_button(
                label=f"📥 TẢI FILE (.TXT)",
                data=master_text,
                file_name=f"DNS_Project_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                mime="text/plain"
            )
            
        st.markdown(f"""<div class="tray-box"><p style="color: {label_color}; font-weight: 900; margin-bottom: 5px;">📁 KHAY DỰ ÁN ĐANG LƯU ({len(st.session_state['project_tray'])} mục)</p></div>""", unsafe_allow_html=True)
        
        with st.expander("📋 BẤM VÀO ĐÂY ĐỂ COPY TOÀN BỘ (Dành cho Điện thoại)"):
            st.text_area("Văn bản tổng hợp (Chạm vào, chọn tất cả và Copy):", value=master_text, height=300)
        
        if st.button("🗑️ XÓA SẠCH KHAY DỰ ÁN ĐỂ LÀM KHÁCH MỚI"):
             st.session_state['project_tray'] = []
             st.rerun()
