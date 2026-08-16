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
    st.session_state['manual_theme'] = "Ban Ngày ☀️" if default_is_daytime else "Ban Đêm 🌙"

selected_theme = st.radio("Theme Switcher", ["Ban Ngày ☀️", "Ban Đêm 🌙"], 
                          index=0 if st.session_state['manual_theme'] == "Ban Ngày ☀️" else 1,
                          horizontal=True, label_visibility="collapsed")
st.session_state['manual_theme'] = selected_theme
is_daytime = (st.session_state['manual_theme'] == "Ban Ngày ☀️")

logo_url = "https://i.postimg.cc/4KNSdqRd/D9754823-56B4-4957-8F90-1EE072CFF5A2.jpg"

if is_daytime:
    app_bg = "#F4F6F9"; element_bg = "#FFFFFF"; text_color = "#1E293B"
    label_color = "#D4AF37"; slogan_color = "#64748B"; border_color = "#D4AF37"
    shadow_3d = "6px 6px 14px rgba(0,0,0,0.06), -6px -6px 14px rgba(255,255,255,0.9)"
    tab_inactive_bg = "#E2E8F0" 
    tab_inactive_color = "#0F172A"  
    watermark_opacity = "0.04"; watermark_blend = "multiply"
    expander_copy_bg = "#F8FAFC"
    subtab_bg = "linear-gradient(145deg, #f0f0f0, #cacaca)"
    subtab_shadow = "5px 5px 12px #bebebe, -5px -5px 12px #ffffff"
    subtab_active_bg = "linear-gradient(145deg, #D4AF37, #B8860B)"
    subtab_active_shadow = "inset 5px 5px 10px #9a7009, inset -5px -5px 10px #fceea5"
else:
    app_bg = "#1E222A"; element_bg = "#252A34"; text_color = "#F1F5F9"
    label_color = "#E5C058"; slogan_color = "#94A3B8"; border_color = "#D4AF37"
    shadow_3d = "6px 6px 14px rgba(0,0,0,0.35), -4px -4px 10px rgba(255,255,255,0.03)"
    tab_inactive_bg = "#1E222A"
    tab_inactive_color = "#FFFFFF"  
    watermark_opacity = "0.08"; watermark_blend = "screen"
    expander_copy_bg = "#1A1D24"
    subtab_bg = "linear-gradient(145deg, #21252e, #1c1f26)"
    subtab_shadow = "5px 5px 12px #15181d, -5px -5px 12px #2d323f"
    subtab_active_bg = "linear-gradient(145deg, #E5C058, #C89B2B)"
    subtab_active_shadow = "inset 5px 5px 10px #a68124, inset -5px -5px 10px #ffdf30"

st.markdown(f"""<div class="watermark-logo"></div>""", unsafe_allow_html=True)

custom_css = f"""
<style>
    header[data-testid="stHeader"] {{ display: none !important; }} footer {{ display: none !important; }}
    .stApp {{ background-color: {app_bg} !important; transition: background-color 0.4s ease; }}
    
    div[data-testid="stSpinner"] {{ background-color: transparent !important; }}
    div[data-testid="stSpinner"] svg circle {{ stroke: {border_color} !important; }}
    div[data-testid="stSpinner"] > div > span, div[data-testid="stSpinner"] p {{
        color: {label_color} !important; font-weight: 900 !important; font-size: 17px !important;
        background-color: transparent !important; text-shadow: 1px 1px 3px rgba(0,0,0,0.5); opacity: 1 !important;
    }}
    
    [data-testid="stExpander"] {{ background-color: {expander_copy_bg} !important; border-radius: 8px; border: 1.5px solid {border_color}; margin-top: 15px; }}
    [data-testid="stExpander"] summary p {{ color: {text_color} !important; font-weight: 800 !important; font-size: 15px; }}
    [data-testid="stExpander"] summary:hover p {{ color: {label_color} !important; }}
    
    .watermark-logo {{
        position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%);
        width: 450px; height: 450px; background-image: url('{logo_url}');
        background-size: cover; background-repeat: no-repeat; background-position: center;
        opacity: {watermark_opacity}; mix-blend-mode: {watermark_blend}; pointer-events: none; z-index: 0;
        border-radius: 50%; mask-image: radial-gradient(circle closest-side, black 65%, transparent 100%);
    }}
    [data-testid="stAppViewBlockContainer"] {{ position: relative; z-index: 10; padding-top: 3rem !important; }}
    div[data-testid="stRadio"] {{
        position: fixed !important; top: 15px !important; right: 15px !important; width: max-content !important;
        z-index: 999999 !important; background-color: {element_bg} !important; border: 1.5px solid {border_color} !important;
        border-radius: 30px !important; padding: 4px 12px !important; box-shadow: {shadow_3d} !important;
    }}
    div[data-testid="stRadio"] label p {{ color: {text_color} !important; font-weight: bold !important; font-size: 13px !important; }}
    .title-brand {{ text-align: center; color: {border_color} !important; font-size: 2.5rem; font-weight: 900; margin-bottom: 5px; letter-spacing: 2px; text-shadow: 0px 4px 12px rgba(212, 175, 55, 0.35); }}
    .slogan {{ text-align: center; color: {slogan_color} !important; font-size: 1.05rem; font-style: italic; margin-bottom: 25px; }}
    label, .stCheckbox > label > div > p, .stRadio > label > div > p {{ color: {label_color} !important; font-weight: bold !important; font-size: 15px !important; }}
    .stTextInput > div > div > input, .stSelectbox > div > div > div, .stSelectbox > div > div > [role="combobox"] {{
        background-color: {element_bg} !important; color: {text_color} !important;
        font-weight: 600 !important; border-radius: 12px !important; border: 1px solid {border_color} !important; box-shadow: {shadow_3d} !important; padding: 12px !important;
    }}
    [data-testid="stFileUploader"] section {{ background-color: {element_bg} !important; border: 1.5px dashed {border_color} !important; border-radius: 15px !important; box-shadow: {shadow_3d} !important; padding: 20px !important; }}
    [data-testid="stFileUploader"] section span, [data-testid="stFileUploader"] section small {{ color: {text_color} !important; font-weight: bold; }}
    [data-testid="stFileUploader"] button, [data-testid="stUploadedFile"] {{ background: linear-gradient(135deg, #E5C058 0%, #B8860B 100%) !important; color: #121418 !important; font-weight: bold !important; border: none !important; }}
    [data-testid="stUploadedFile"] {{ border-radius: 8px !important; }}
    [data-testid="stUploadedFile"] div, [data-testid="stUploadedFile"] span {{ color: #121418 !important; font-weight: bold !important; }}
    .stButton > button {{ width: 100%; height: 58px; font-size: 19px; font-weight: 900; background: linear-gradient(135deg, #E5C058 0%, #B8860B 100%) !important; color: #121418 !important; border: 1px solid #F7E08B !important; border-radius: 12px !important; box-shadow: 0 8px 18px rgba(184, 134, 11, 0.35); margin-top: 15px; }}
    
    div[data-testid="stTabs"] button[data-baseweb="tab"] p, 
    div[data-testid="stTabs"] button[data-baseweb="tab"] span, 
    div[data-testid="stTabs"] button[data-baseweb="tab"] div {{
        color: {tab_inactive_color} !important;
        font-weight: 800 !important;
        opacity: 1 !important;
    }}
    div[data-testid="stTabs"] button[data-baseweb="tab"]:hover p, 
    div[data-testid="stTabs"] button[data-baseweb="tab"]:hover span {{
        color: {label_color} !important;
    }}
    div[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] p, 
    div[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] span,
    div[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] div {{
        color: #121418 !important;
        font-weight: 900 !important;
    }}
    div[data-testid="stTabs"] button[data-baseweb="tab"] {{
        background-color: {tab_inactive_bg} !important;
        border: 2px solid rgba(212, 175, 55, 0.6) !important;
        border-bottom: none !important;
        border-radius: 14px 14px 0px 0px !important;
        padding: 12px 18px !important;
        box-shadow: {shadow_3d} !important;
    }}
    div[data-testid="stTabs"] button[aria-selected="true"] {{
        background: linear-gradient(145deg, #E5C058, #C89B2B) !important;
        border: 2px solid #F7E08B !important;
        border-bottom: none !important;
        transform: translateY(-6px);
        box-shadow: 0px -6px 15px rgba(200, 155, 43, 0.4) !important;
        z-index: 10;
    }}
    
    div[data-testid="stTabs"] div[data-testid="stTabs"] [data-baseweb="tab-list"] {{ display: flex; justify-content: space-between; background: transparent; padding: 15px 0; border: none; }}
    div[data-testid="stTabs"] div[data-testid="stTabs"] button[data-baseweb="tab"] {{
        flex: 1; margin: 0 8px; border-radius: 12px !important; padding: 16px 10px !important; text-align: center;
        background: {subtab_bg} !important;
        box-shadow: {subtab_shadow} !important;
        border: 1.5px solid rgba(212, 175, 55, 0.3) !important;
        opacity: 1 !important;
    }}
    div[data-testid="stTabs"] div[data-testid="stTabs"] button[data-baseweb="tab"] p {{
        color: {text_color} !important; font-size: 16px !important; font-weight: 900 !important;
    }}
    div[data-testid="stTabs"] div[data-testid="stTabs"] button[aria-selected="true"] {{
        background: {subtab_active_bg} !important;
        box-shadow: {subtab_active_shadow} !important;
        border: 1.5px solid {border_color} !important;
    }}
    div[data-testid="stTabs"] div[data-testid="stTabs"] button[aria-selected="true"] p {{ color: #121418 !important; }}

    .dns-card {{ background-color: {element_bg} !important; border: 2px solid {border_color} !important; border-radius: 0px 15px 15px 15px; padding: 25px; box-shadow: {shadow_3d} !important; position: relative; z-index: 2; margin-bottom: 20px; }}
    .dns-logo-3d {{ max-width: 90px; border-radius: 10px; border: 2px solid {border_color}; margin-bottom: 15px; display: block; margin-left: auto; margin-right: auto; }}
    .dns-text {{ font-family: 'Consolas', monospace; font-size: 15px; line-height: 1.7; color: {text_color} !important; }}
    .dns-footer {{ text-align: center; border-top: 1px dashed {border_color}; padding-top: 15px; margin-top: 25px; color: {slogan_color}; font-size: 13px; display: flex; justify-content: space-between; align-items: center; }}
    .warning-box {{ border-left: 5px solid #FF4D4D; background-color: rgba(255,77,77,0.15); padding: 12px 15px; border-radius: 8px; margin-bottom: 12px; color: #FF4D4D !important; font-weight: bold; }}
    
    .dns-expander {{ margin-bottom: 12px; margin-top: 10px; border-radius: 10px; background: {element_bg}; overflow: hidden; box-shadow: {subtab_shadow}; border: 1px solid rgba(212, 175, 55, 0.3); }}
    .dns-expander summary {{ padding: 15px; font-weight: 800; color: {label_color}; background: {subtab_bg}; cursor: pointer; list-style: none; font-size: 15.5px; transition: all 0.2s; }}
    .dns-expander summary::-webkit-details-marker {{ display: none; }}
    .dns-expander[open] summary {{ border-bottom: 1px dashed {border_color}; background: {subtab_active_bg}; color: #121418 !important; box-shadow: {subtab_active_shadow}; }}
    .expander-content {{ padding: 15px; background: {app_bg}; color: {text_color} !important; line-height: 1.6; font-size: 14.5px; border-top: 1px solid rgba(212, 175, 55, 0.1); }}
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
        "5. Dự án Video: So Sánh Auto vs Manual DNS (Dành cho Team Content)"
    ]
)

col1, col2 = st.columns(2)
with col1:
    player_info = st.text_input("👤 Tên Cầu thủ/Sơ đồ (Bỏ trống nếu không cần):", placeholder="Ví dụ: Roberto Carlos, 4-2-1-3...")
    ecosystem = st.selectbox("🌐 Chọn hệ sinh thái (SIM AI / PvP):", ["SIM AI", "PvP"], index=1)
with col2:
    uploaded_players = st.file_uploader("📸 1. Tải ảnh Cầu thủ (eFHUB/In-game):", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True, key="player_imgs")
    uploaded_managers = st.file_uploader("📸 2. Tải ảnh HLV (Manager Buff):", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True, key="manager_imgs")

# ---------------------------------------------------------
# 3. HÀM XỬ LÝ DỮ LIỆU
# ---------------------------------------------------------
def render_expander_from_json(items):
    if not items or len(items) == 0: 
        return "<p style='color: #64748B; font-style: italic; text-align: center; padding: 20px;'>Chưa có dữ liệu phân bổ cho tuyến này.</p>"
    html_out = ""
    for item in items:
        title = item.get("vitri", "Vị trí")
        loai = item.get("loai", "Đá chính")
        style = item.get("style", "")
        vaitro = item.get("vaitro", "")
        content = f"<strong>Phân loại:</strong> {loai}<br><strong>Style đề xuất:</strong> <span style='color:{label_color}; font-weight:800;'>{style}</span><br><strong>Vai trò chiến thuật:</strong> {vaitro}"
        html_out += f'<details class="dns-expander"><summary>{title} ({loai})</summary><div class="expander-content"><p>🔹 {content}</p></div></details>'
    return html_out

def format_in_game_json(data):
    if not data: return ""
    atk_list = data.get("individual_instructions", {}).get("tan_cong", [])
    def_list = data.get("individual_instructions", {}).get("phong_ngu", [])
    atk_str = "<br>".join([f"🔸 Gán <strong>{i.get('lenh_duoc_chon', '')}</strong> cho {i.get('ap_dung_cho_vi_tri', '')}" for i in atk_list]) if isinstance(atk_list, list) else str(atk_list)
    def_str = "<br>".join([f"🔸 Gán <strong>{i.get('lenh_duoc_chon', '')}</strong> cho {i.get('ap_dung_cho_vi_tri', '')}" for i in def_list]) if isinstance(def_list, list) else str(def_list)
    if not atk_str: atk_str = "Không gán lệnh tấn công."
    if not def_str: def_str = "Không gán lệnh phòng ngự."

    html_out = "<strong>1. Cài đặt Lệnh Cá nhân (Individual Instructions):</strong><br><br>"
    html_out += f"🔹 <strong style='color:#FF4D4D;'>Tấn công:</strong><br><span style='margin-left: 20px; display: block;'>{atk_str}</span><br>"
    html_out += f"🔹 <strong style='color:#4D94FF;'>Phòng ngự:</strong><br><span style='margin-left: 20px; display: block;'>{def_str}</span><br><br>"
    html_out += "<strong>2. Kịch bản Thay người (Mental Level):</strong><br><br>"
    html_out += f"🔹 <strong>Start Game (Cân bằng):</strong> {data.get('k1', '')}<br>"
    html_out += f"🔹 <strong>Đang dẫn bàn (Nấc Xanh):</strong> {data.get('k2', '')}<br>"
    html_out += f"🔹 <strong>Bị dẫn bàn (Nấc Đỏ):</strong> {data.get('k3', '')}"
    return html_out

def translate_json_to_markdown(json_23, json_ingame):
    md_out = "=== QUY HOẠCH 23 CẦU THỦ ===\n\n"
    if json_23:
        for tuyen in ["FW", "MF", "DF", "GK"]:
            if tuyen in json_23:
                md_out += f"--- Tuyến {tuyen} ---\n"
                for item in json_23[tuyen]:
                    md_out += f"- {item.get('vitri', '')} ({item.get('loai', '')}): Style {item.get('style', '')}. Vai trò: {item.get('vaitro', '')}\n"
                md_out += "\n"
    md_out += "=== CẨM NANG IN-GAME ===\n\n"
    if json_ingame:
        atk_list = json_ingame.get("individual_instructions", {}).get("tan_cong", [])
        def_list = json_ingame.get("individual_instructions", {}).get("phong_ngu", [])
        atk_str = ", ".join([f"{i.get('lenh_duoc_chon', '')} cho {i.get('ap_dung_cho_vi_tri', '')}" for i in atk_list]) if isinstance(atk_list, list) else str(atk_list)
        def_str = ", ".join([f"{i.get('lenh_duoc_chon', '')} cho {i.get('ap_dung_cho_vi_tri', '')}" for i in def_list]) if isinstance(def_list, list) else str(def_list)
        md_out += f"1. Individual Instructions:\n- Tấn công: {atk_str}\n- Phòng ngự: {def_str}\n\n"
        md_out += f"2. Kịch bản Thay người:\n- Mặc định: {json_ingame.get('k1', '')}\n- Nấc Xanh: {json_ingame.get('k2', '')}\n- Nấc Đỏ: {json_ingame.get('k3', '')}"
    return md_out

# ---------------------------------------------------------
# 4. LÕI TƯ DUY AI CHUYÊN SÂU (TỐI ƯU CƠ CHẾ SA BÀN & OCR)
# ---------------------------------------------------------
def execute_tactical_analysis(img_list, p_info, eco, mode):
    try:
        api_key = st.secrets.get("GEMINI_API_KEY")
        if not api_key: return "[LỖI CẤU HÌNH]: Không tìm thấy GEMINI_API_KEY!"
        client = genai.Client(api_key=api_key)
        
        hard_rules = """
        [QUY TẮC BẮT BUỘC CHUNG]:
        1. Tuyệt đối không dùng HTML. Không xuất hiện chữ 'CẢNH BÁO TỪ CHỐI DỰ ÁN VIDEO' trong nội dung phân tích xuất ra.
        2. Tôn trọng Style Cơ bản In-game gốc. 100% sử dụng THUẬT NGỮ TIẾNG ANH cho chỉ số. Không dịch ra tiếng Việt.
        """

        if "1" in mode:
            tab1_cmd = "Thẩm định thẻ Auto này với triết lý HLV. Kết luận rõ: Phù hợp hay Lệch pha. Đánh giá ưu nhược điểm chi tiết."
            tab2_cmd = "CẢNH BÁO TỪ CHỐI DO ĐANG DÙNG THẺ AUTO."
            tab3_cmd = "CẢNH BÁO TỪ CHỐI DO ĐANG DÙNG THẺ AUTO."
            tab4_cmd = """
            CẨM NANG IN-GAME:
            1. Gán Lệnh Cá Nhân (Individual Instructions):
            - Tấn công: CHỈ CHỌN 'Defensive' HOẶC 'Anchoring'.
            - Phòng ngự: CHỈ CHỌN 'Tight Marking', 'Man Marking', HOẶC 'Counter Target'.
            (KHÔNG DÙNG DEEP LINE HOẶC CÁC LỆNH KHÁC).
            2. 3 kịch bản Cài đặt In-game: Start Game, Tấn công tổng lực, Tử thủ.
            """
            
        elif "2" in mode:
            tab1_cmd = """
            1. Thẩm định vai trò cầu thủ trên sân theo đúng Sơ đồ & Triết lý của HLV.
            2. Nhận diện Slot Booster: 
            [LỆNH CẤM THÉP]: Nếu thẻ có Slot Booster thứ 2, BẠN CHỈ ĐƯỢC ĐỀ XUẤT BOOSTER +1 (Ví dụ: Shooting +1, Technique +1, Agility +1, Shutting Down +1...). TUYỆT ĐỐI CẤM bịa ra Booster +2.
            """
            tab2_cmd = """
            TƯ DUY SA BÀN BẬC THẦY VÀ QUY HOẠCH PP:
            [NẾU THẺ ĐÃ BUILD SẴN TRÊN ẢNH]:
            1. Bạn phải đóng vai trò MÁY QUÉT OCR. Nhìn vào các thanh trượt bên trái để lấy 'Số Nấc', nhìn vào cột xanh/đỏ bên phải để lấy 'Chỉ số hiển thị thực tế'. TUYỆT ĐỐI KHÔNG TỰ TÍNH LẠI CÁC SỐ ĐÓ.
            2. 100% TÊN CHỈ SỐ LÀ TIẾNG ANH (Speed, Acceleration, Offensive Awareness, Finishing, Passing...).

            [CỐT LÕI CHUYÊN MÔN - BẮT BUỘC CÓ Ở MỖI NHÁNH]:
            Không chỉ liệt kê con số vô hồn. Hãy chứng minh bạn là một Chuyên Gia. Dưới mỗi nhánh nâng cấp, BẮT BUỘC viết [LẬP LUẬN TACTICAL SÁT THƯƠNG]. 
            Bạn phải giải thích vì sao mức chỉ số đó lại tạo ra độ "sát thương" cực cao cho lối đá của HLV. (Ví dụ: Possession Game cần chuyền chọt thoát pressing; Quick Counter cần Speed/Acceleration để đâm nách cắt mặt...).
            Dùng ngôn từ sắc bén của dân làm chiến thuật.
            
            Format:
            - **[Tên nhánh Tiếng Anh]**: [X] Nấc -> [Chỉ số 1]: [Số chuẩn] | [Chỉ số 2]: [Số chuẩn].
              [LẬP LUẬN TACTICAL SÁT THƯƠNG]: [Phân tích logic cực nét theo Meta game và HLV].
            """
            tab3_cmd = "CẢNH BÁO TỪ CHỐI DÀNH CHO DỰ ÁN VIDEO."
            tab4_cmd = """
            1. Gán Lệnh Cá Nhân (Individual Instructions):
            - Tấn công: CHỈ CHỌN 'Defensive' HOẶC 'Anchoring'.
            - Phòng ngự: CHỈ CHỌN 'Tight Marking', 'Man Marking', HOẶC 'Counter Target'.
            2. Đề xuất Top 5 Skills bổ sung then chốt nhất kèm lý do chuyên môn ngắn gọn.
            """
            
        elif "3" in mode:
            tab1_cmd = "Phân tích Sơ đồ Tấn Công và Phòng Ngự."
            tab2_cmd = "CẢNH BÁO TỪ CHỐI DÀNH CHO BUILD 23 NGƯỜI."
            tab3_cmd = "CẢNH BÁO TỪ CHỐI."
            tab4_cmd = "CẢNH BÁO TỪ CHỐI."
            
        elif "4" in mode:
            tab1_cmd = "Phân tích Triết lý HLV. Vẽ Sơ đồ Tấn công và Sơ đồ Phòng ngự (Viết văn bản thường)."
            tab2_cmd = """
            QUY HOẠCH ĐỦ 23 CẦU THỦ. CHỈ GHI VỊ TRÍ, STYLE VÀ VAI TRÒ. BẮT BUỘC TRẢ VỀ ĐÚNG ĐỊNH DẠNG JSON.
            ```json
            {
              "FW": [
                {"vitri": "CF", "loai": "Đá chính", "style": "Goal Poacher", "vaitro": "Chạy chỗ cắt mặt..."}
              ],
              "MF": [
                {"vitri": "DMF", "loai": "Đá chính", "style": "Anchor Man", "vaitro": "Đánh chặn..."}
              ],
              "DF": [
                {"vitri": "CB", "loai": "Đá chính", "style": "Build Up", "vaitro": "Bọc lót..."}
              ],
              "GK": [
                {"vitri": "GK", "loai": "Đá chính", "style": "Offensive GK", "vaitro": "Cản phá..."}
              ]
            }
            ```
            """
            tab3_cmd = "CẢNH BÁO TỪ CHỐI."
            tab4_cmd = """
            CẨM NANG IN-GAME CHIẾN THUẬT. BẮT BUỘC TRẢ VỀ JSON.
            ```json
            {
              "individual_instructions": {
                "tan_cong": [
                  {"lenh_duoc_chon": "Defensive", "ap_dung_cho_vi_tri": "DMF"}
                ],
                "phong_ngu": [
                  {"lenh_duoc_chon": "Counter Target", "ap_dung_cho_vi_tri": "CF"}
                ]
              },
              "k1": "Đội hình xuất phát...",
              "k2": "Rút [Vị trí] thay [Vị trí phòng ngự]",
              "k3": "Rút [Vị trí] thay [Vị trí tấn công]"
            }
            ```
            """
        else:
            tab1_cmd = "CẢNH BÁO TỪ CHỐI DÀNH CHO DỰ ÁN VIDEO."
            tab2_cmd = "CẢNH BÁO TỪ CHỐI DÀNH CHO DỰ ÁN VIDEO."
            tab3_cmd = "SO SÁNH AUTO VS MANUAL DNS. Lập luận phân tích [CHÊNH LỆCH CHỈ SỐ], [LẬP LUẬN CHUYÊN MÔN]."
            tab4_cmd = "CẢNH BÁO TỪ CHỐI DÀNH CHO DỰ ÁN VIDEO."

        system_instruction = f"""
        {hard_rules}
        CHIA BÁO CÁO THÀNH 4 PHẦN NGĂN CÁCH NHAU BỞI DẤU "===" NẰM ĐỘC LẬP TRÊN 1 DÒNG.

        PHẦN 1: THẨM ĐỊNH TƯƠNG THÍCH & TRIẾT LÝ
        {tab1_cmd}
        ===
        PHẦN 2: PHÂN BỔ PP & QUY HOẠCH
        {tab2_cmd}
        ===
        PHẦN 3: SO SÁNH AUTO VS THỦ CÔNG & BUFF HLV
        {tab3_cmd}
        ===
        PHẦN 4: CẨM NANG IN-GAME
        {tab4_cmd}
        """
        
        config = types.GenerateContentConfig(system_instruction=system_instruction, temperature=0.1)
        context_prompt = f"Thông tin: {p_info} | Hệ: {eco} | Chế độ: {mode}"
        contents = [context_prompt] + img_list
        
        candidate_models = ['gemini-3.6-flash']
        
        last_error = ""
        for model_name in candidate_models:
            for attempt in range(2):
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=contents,
                        config=config
                    )
                    if response and response.text:
                        return response.text
                except APIError as api_err:
                    last_error = str(api_err)
                    if "503" in last_error or "429" in last_error:
                        time.sleep(1.5)
                        continue
                    else:
                        break
                except Exception as e:
                    last_error = str(e)
                    time.sleep(1.0)
                    continue

        return f"[LỖI HỆ THỐNG]: Server Google quá tải tạm thời ({last_error}). Vui lòng bấm 'BẮT ĐẦU PHÂN TÍCH' lại sau vài giây!"
    except Exception as e:
        return f"[LỖI HỆ THỐNG]: {str(e)}"

# ---------------------------------------------------------
# 5. RENDER GIAO DIỆN & LỌC SẠCH VĂN BẢN
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
                
            st.session_state['raw_report'] = execute_tactical_analysis(images_to_send, player_info, ecosystem, analysis_mode)
            st.session_state['report_time'] = vn_time_now.strftime("%d/%m/%Y | %H:%M:%S")
            images_to_send.clear(); gc.collect()

if 'raw_report' in st.session_state:
    mode_selected = analysis_mode[0]
    raw_text = st.session_state['raw_report'].replace("⛔ ", "").replace("*", "")
    
    parts = raw_text.split("===")
    
    if mode_selected == "2" and len(parts) > 2:
        parts[2] = "\n\nCẢNH BÁO TỪ CHỐI DÀNH CHO DỰ ÁN VIDEO.\n\n"
        
    tab1_c = parts[0].strip() if len(parts) > 0 else ""
    tab2_c = parts[1].strip() if len(parts) > 1 else ""
    tab3_c = parts[2].strip() if len(parts) > 2 else ""
    tab4_c = parts[3].strip() if len(parts) > 3 else ""
    
    # Rà soát lỗi AI "nhả nhầm" câu cảnh báo sang Tab 2
    if mode_selected == "2":
        tab2_c = re.sub(r'CẢNH BÁO TỪ CHỐI.*', '', tab2_c, flags=re.IGNORECASE).strip()
    
    report_time = st.session_state.get('report_time', vn_time_now.strftime("%d/%m/%Y | %H:%M:%S"))
    footer_text_color = "#64748B" if is_daytime else "#94A3B8"
    
    def format_tab_content(content):
        # Bộ lọc cực thông minh: Chỉ bắt chính xác thông báo lỗi từ chối, không "giết nhầm" tab 2
        if "CẢNH BÁO TỪ CHỐI" in content and len(content) < 150:
            return f"<div class='warning-box'>⛔ Tính năng này đã bị khóa do không thuộc phạm vi của Chế độ phân tích hiện tại.</div>"
        html_content = content.replace('\n', '<br>')
        return f"""<div class="dns-card">
            <img src="{logo_url}" class="dns-logo-3d">
            <div class="dns-text">{html_content}</div>
            <div class="dns-footer">
                <span style="color: {footer_text_color}; font-style: italic; font-weight: 600;">Đồng bộ lúc: {report_time}</span>
                <span style="color: {label_color}; font-weight: 900;">DNS TACTICAL ARCHITECT <br> © 2026 DN SIM MY LEAGUE. All rights reserved.</span>
            </div>
        </div>"""

    def extract_json(text):
        try:
            json_str = re.search(r'\{.*\}', text, re.DOTALL).group()
            return json.loads(json_str)
        except:
            return None

    if mode_selected == "4":
        t1, t2, t4 = st.tabs(["🪪 THẨM ĐỊNH & TRIẾT LÝ", "🛠️ QUY HOẠCH 23 CẦU THỦ", "🎯 CÀI ĐẶT & KỸ NĂNG SA BÀN"])
        with t1: st.markdown(format_tab_content(tab1_c), unsafe_allow_html=True)
        
        json_data_23 = extract_json(tab2_c)
        json_data_ingame = extract_json(tab4_c)
        
        with t2: 
            if json_data_23:
                s1, s2, s3, s4 = st.tabs(["⚽ FW", "🎯 MF", "🛡️ DF", "🧤 GK"])
                with s1: st.markdown(render_expander_from_json(json_data_23.get("FW", [])), unsafe_allow_html=True)
                with s2: st.markdown(render_expander_from_json(json_data_23.get("MF", [])), unsafe_allow_html=True)
                with s3: st.markdown(render_expander_from_json(json_data_23.get("DF", [])), unsafe_allow_html=True)
                with s4: st.markdown(render_expander_from_json(json_data_23.get("GK", [])), unsafe_allow_html=True)
            else:
                st.markdown(format_tab_content("Lỗi truy xuất dữ liệu từ Sa bàn. Vui lòng phân tích lại."), unsafe_allow_html=True)
                
            st.markdown(f"""<div class="dns-card" style="margin-top: 10px; padding: 15px;">
                <div class="dns-footer" style="margin-top: 0; padding-top:0; border:none;">
                    <span style="color: {footer_text_color}; font-style: italic; font-weight: 600;">Đồng bộ lúc: {report_time}</span>
                    <span style="color: {label_color}; font-weight: 900;">DNS TACTICAL ARCHITECT <br> © 2026 DN SIM MY LEAGUE. All rights reserved.</span>
                </div>
            </div>""", unsafe_allow_html=True)
                
        with t4: 
            if json_data_ingame:
                st.markdown(format_tab_content(format_in_game_json(json_data_ingame)), unsafe_allow_html=True)
            else:
                st.markdown(format_tab_content(tab4_c), unsafe_allow_html=True)
                
        with st.expander("Bấm vào đây để Copy văn bản thô (Dành cho Team Content)"):
             markdown_sach = f"{tab1_c}\n\n{translate_json_to_markdown(json_data_23, json_data_ingame)}"
             st.text_area("Văn bản gốc (Markdown Dịch Sạch):", value=markdown_sach, height=350)

    elif mode_selected == "2":
        t1, t2, t4 = st.tabs(["🪪 THẨM ĐỊNH & BOOSTER", "🛠️ BẢNG BUILD PP", "🎯 LỆNH IN-GAME & TOP 5 SKILLS"])
        with t1: st.markdown(format_tab_content(tab1_c), unsafe_allow_html=True)
        with t2: st.markdown(format_tab_content(tab2_c), unsafe_allow_html=True)
        with t4: st.markdown(format_tab_content(tab4_c), unsafe_allow_html=True)
        
        clean_raw = f"{tab1_c}\n\n{tab2_c}\n\n{tab4_c}"
        with st.expander("Bấm vào đây để Copy văn bản thô (Dành cho Team Content)"):
             st.text_area("Văn bản gốc:", value=clean_raw.strip(), height=300)
             
    else:
        t1, t2, t4 = st.tabs(["🪪 THẨM ĐỊNH & TRIẾT LÝ", "🛠️ PHÂN BỔ PP", "🎯 CÀI ĐẶT & KỸ NĂNG SA BÀN"])
        with t1: st.markdown(format_tab_content(tab1_c), unsafe_allow_html=True)
        with t2: st.markdown(format_tab_content(tab2_c), unsafe_allow_html=True)
        with t4: st.markdown(format_tab_content(tab4_c), unsafe_allow_html=True)
        
        clean_raw = raw_text.replace("===", "\n\n")
        with st.expander("Bấm vào đây để Copy văn bản thô (Dành cho Team Content)"):
             st.text_area("Văn bản gốc:", value=clean_raw.strip(), height=250)
