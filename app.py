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

# LINK LOGO PNG TRONG SUỐT CỦA BOSS
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
    [data-testid="stExpander"] {{ background-color: {expander_copy_bg} !important; border-radius: 8px; border: 1.5px solid {border_color}; margin-top: 15px; }}
    [data-testid="stExpander"] summary p {{ color: {text_color} !important; font-weight: 800 !important; font-size: 15px; }}
    
    /* ĐÃ FIX HIỂN THỊ LOGO TRÊN CẢ MOBILE VÀ LAPTOP */
    .stApp::before {{ 
        content: "";
        position: fixed; 
        top: 50%; 
        left: 50%; 
        transform: translate(-50%, -50%); 
        width: 85vw; 
        max-width: 450px; 
        height: 85vw; 
        max-height: 450px; 
        background-image: url('{logo_url}'); 
        background-size: contain; 
        background-repeat: no-repeat; 
        background-position: center; 
        opacity: 0.15; 
        pointer-events: none; 
        z-index: 999999; 
    }}
    
    [data-testid="stAppViewBlockContainer"] {{ position: relative; z-index: 10; padding-top: 3rem !important; }}
    div[data-testid="stRadio"] {{ position: fixed !important; top: 15px !important; right: 15px !important; z-index: 999999 !important; background-color: {element_bg} !important; border: 1.5px solid {border_color} !important; border-radius: 30px !important; padding: 4px 12px !important; box-shadow: {shadow_3d} !important; }}
    .title-brand {{ text-align: center; color: {border_color} !important; font-size: 2.5rem; font-weight: 900; margin-bottom: 5px; letter-spacing: 2px; }}
    .slogan {{ text-align: center; color: {slogan_color} !important; font-size: 1.05rem; font-style: italic; margin-bottom: 25px; }}
    label {{ color: {label_color} !important; font-weight: bold !important; font-size: 15px !important; }}
    .stTextInput>div>div>input, .stSelectbox>div>div>div {{ background-color: {element_bg} !important; color: {text_color} !important; font-weight: 600 !important; border-radius: 12px !important; border: 1px solid {border_color} !important; }}
    [data-testid="stFileUploader"] section {{ background-color: {element_bg} !important; border: 1.5px dashed {border_color} !important; border-radius: 15px !important; }}
    [data-testid="stFileUploader"] button {{ background: linear-gradient(135deg, #E5C058, #B8860B) !important; color: #121418 !important; font-weight: bold !important; }}
    .stButton > button {{ width: 100%; height: 58px; font-size: 19px; font-weight: 900; background: linear-gradient(135deg, #E5C058, #B8860B) !important; color: #121418 !important; border-radius: 12px !important; }}
    div[data-testid="stTabs"] button[data-baseweb="tab"] {{ background-color: {tab_inactive_bg} !important; border: 2px solid rgba(212, 175, 55, 0.6) !important; border-bottom: none !important; border-radius: 14px 14px 0px 0px !important; }}
    div[data-testid="stTabs"] button[aria-selected="true"] {{ background: linear-gradient(145deg, #E5C058, #C89B2B) !important; }}
    div[data-testid="stTabs"] div[data-testid="stTabs"] button[data-baseweb="tab"] {{ background: {subtab_bg} !important; border-radius: 12px !important; }}
    div[data-testid="stTabs"] div[data-testid="stTabs"] button[aria-selected="true"] {{ background: {subtab_active_bg} !important; border: 1.5px solid {border_color} !important; }}
    .dns-card {{ background-color: {element_bg} !important; border: 2px solid {border_color} !important; border-radius: 0px 15px 15px 15px; padding: 25px; box-shadow: {shadow_3d} !important; position: relative; z-index: 2; margin-bottom: 20px; }}
    .dns-logo-3d {{ max-width: 90px; border-radius: 10px; border: 2px solid {border_color}; margin-bottom: 15px; display: block; margin-left: auto; margin-right: auto; }}
    .dns-text {{ font-family: 'Consolas', monospace; font-size: 15px; line-height: 1.7; color: {text_color} !important; }}
    .dns-footer {{ text-align: center; border-top: 1px dashed {border_color}; padding-top: 15px; margin-top: 25px; color: {slogan_color}; font-size: 13px; display: flex; justify-content: space-between; }}
    .warning-box {{ border-left: 5px solid #FF4D4D; background-color: rgba(255,77,77,0.15); padding: 12px 15px; border-radius: 8px; color: #FF4D4D !important; font-weight: bold; margin-bottom: 15px; }}
    .dns-expander summary {{ padding: 15px; font-weight: 800; color: {label_color}; background: {subtab_bg}; cursor: pointer; border-radius: 10px; border: 1px solid rgba(212, 175, 55, 0.3); }}
    .expander-content {{ padding: 15px; background: {app_bg}; color: {text_color} !important; font-size: 14.5px; border-top: 1px solid rgba(212, 175, 55, 0.1); }}
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
with col2:
    uploaded_players = st.file_uploader("📸 1. Tải ảnh Cầu thủ (eFHUB/In-game):", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)
    uploaded_managers = st.file_uploader("📸 2. Tải ảnh HLV (Manager Buff):", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)

# ---------------------------------------------------------
# 3. HÀM KẾT XUẤT JSON 
# ---------------------------------------------------------
def render_expander_from_json(items):
    if not items or len(items) == 0: 
        return "<p style='color: #64748B; font-style: italic; text-align: center;'>Chưa có dữ liệu phân bổ.</p>"
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
    atk_list = data.get("individual_instructions", {}).get("tan_cong", [])
    def_list = data.get("individual_instructions", {}).get("phong_ngu", [])
    atk_str = "<br>".join([f"🔸 Gán <strong>{i.get('lenh_duoc_chon', '')}</strong> cho {i.get('ap_dung_cho_vi_tri', '')}" for i in atk_list]) if isinstance(atk_list, list) else str(atk_list)
    def_str = "<br>".join([f"🔸 Gán <strong>{i.get('lenh_duoc_chon', '')}</strong> cho {i.get('ap_dung_cho_vi_tri', '')}" for i in def_list]) if isinstance(def_list, list) else str(def_list)
    html_out = "<strong>1. Cài đặt Lệnh Cá nhân (Individual Instructions):</strong><br><br>"
    html_out += f"🔹 <strong style='color:#FF4D4D;'>Tấn công:</strong><br><span style='margin-left: 20px; display: block;'>{atk_str}</span><br>"
    html_out += f"🔹 <strong style='color:#4D94FF;'>Phòng ngự:</strong><br><span style='margin-left: 20px; display: block;'>{def_str}</span><br><br>"
    html_out += "<strong>2. Kịch bản Thay người (Mental Level):</strong><br><br>"
    html_out += f"🔹 <strong>Start Game:</strong> {data.get('k1', '')}<br>"
    html_out += f"🔹 <strong>Đang dẫn bàn (Nấc Xanh):</strong> {data.get('k2', '')}<br>"
    html_out += f"🔹 <strong>Bị dẫn bàn (Nấc Đỏ):</strong> {data.get('k3', '')}"
    return html_out

# ---------------------------------------------------------
# 4. LÕI TƯ DUY AI (V1.1 - CHỐNG LỖI LOGIC TỰ VẢ)
# ---------------------------------------------------------
def execute_tactical_analysis(img_list, p_info, eco, mode):
    try:
        api_key = st.secrets.get("GEMINI_API_KEY")
        if not api_key: return "[LỖI CẤU HÌNH]: Không tìm thấy GEMINI_API_KEY!"
        client = genai.Client(api_key=api_key)
        
        hard_rules = """
        [LUẬT THÉP BẬT TẮT META - CẤM LỖI LOGIC TỰ VẢ]:
        1. LOGIC ĐỒNG NHẤT CHIẾN THUẬT (QUAN TRỌNG NHẤT):
           - KHÁM HLV (Sa bàn): CHỈ tập trung vào Sơ đồ, Triết lý. TUYỆT ĐỐI CẤM đề xuất Slot Booster (Crafting) hay bóp quỹ PP cho HLV.
           - KHÁM CẦU THỦ (PP): CHỈ tập trung vào thông số cá nhân, Hitbox, Sải chân, PP.
           - SỰ LOGIC TỰ NHIÊN: Nếu HLV đá Possession Game (Kiểm soát) -> Mọi lệnh cá nhân & kỹ năng (Skills) đề xuất PHẢI phục vụ bóng ngắn, ban bật. TUYỆT ĐỐI CẤM đề xuất phất bóng bổng (Lofted Pass) cho sơ đồ Possession.
        2. QUY TẮC NGÔN NGỮ ZERO-FLUFF: Không dùng HTML. 100% Tên chỉ số in-game phải ghi Tiếng Anh (Speed, Finishing, Defensive Awareness...). Không bao giờ dịch ra Tiếng Việt.
        3. LỆNH CÁ NHÂN IN-GAME CHUẨN META:
           - Tấn công: CHỈ CHỌN 'Defensive' HOẶC 'Anchoring'.
           - Phòng ngự: CHỈ CHỌN 'Tight Marking', 'Man Marking', HOẶC 'Counter Target'.
        """

        if "1" in mode:
            tab1_cmd = "Đánh giá Phôi Auto 5 chiều (Style, Hitbox, Skills, Form). KẾT LUẬN RÕ: Hợp hay Loại."
            tab2_cmd = "CẢNH BÁO TỪ CHỐI DO ĐANG DÙNG THẺ AUTO."
            tab3_cmd = "CẢNH BÁO TỪ CHỐI DO ĐANG DÙNG THẺ AUTO."
            tab4_cmd = "Lệnh cá nhân In-game & 3 kịch bản nấc tâm lý."
            
        elif "2" in mode:
            tab1_cmd = "Đánh giá sự tương thích của Cầu thủ trong sơ đồ. Đề xuất Slot Booster (Crafting +1) phù hợp với thẻ cầu thủ."
            tab2_cmd = "TỰ ĐỘNG BUILD TỐI ƯU CHỈ SỐ BẰNG TIẾNG ANH. Giải thích [LẬP LUẬN TACTICAL SÁT THƯƠNG] ở mỗi nhánh. Xài hết sạch quỹ PP."
            tab3_cmd = "CẢNH BÁO TỪ CHỐI DÀNH CHO DỰ ÁN VIDEO."
            tab4_cmd = "Gán Lệnh Cá Nhân phù hợp lối chơi và Đề xuất Top 5 Skills cho cầu thủ."
            
        elif "3" in mode:
            tab1_cmd = "Phân tích HLV: Triết lý chủ đạo, Sơ đồ Tấn Công, Sơ đồ Phòng Ngự. Tiêu chuẩn Hitbox yêu cầu. KHÔNG NHẮC TỚI BOOSTER CẦU THỦ."
            tab2_cmd = "CẢNH BÁO TỪ CHỐI: Tính năng này chỉ dành cho Thẩm định Cầu thủ, không áp dụng cho HLV."
            tab3_cmd = "CẢNH BÁO TỪ CHỐI."
            tab4_cmd = "CẢNH BÁO TỪ CHỐI."
            
        elif "4" in mode:
            tab1_cmd = "Phân tích Triết lý HLV và vẽ sa bàn Công/Thủ."
            tab2_cmd = """
            QUY HOẠCH 23 CẦU THỦ (11 CHÍNH + 12 DỰ BỊ). KHÔNG NÊU TÊN NGOÀI ĐỜI. BẮT BUỘC TRẢ VỀ ĐÚNG FORMAT JSON DƯỚI ĐÂY BÊN TRONG CẶP DẤU ```json VÀ ```. TUYỆT ĐỐI KHÔNG THÊM CHỮ BÊN NGOÀI.
            ```json
            {
              "FW": [{"vitri": "CF", "loai": "Đá chính", "style": "Goal Poacher", "vaitro": "Mũi khoan..."}],
              "MF": [{"vitri": "DMF", "loai": "Đá chính", "style": "Anchor Man", "vaitro": "Mỏ neo..."}],
              "DF": [{"vitri": "CB", "loai": "Đá chính", "style": "Build Up", "vaitro": "Triển khai..."}],
              "GK": [{"vitri": "GK", "loai": "Đá chính", "style": "Offensive GK", "vaitro": "Băng ra..."}]
            }
            ```
            """
            tab3_cmd = "CẢNH BÁO TỪ CHỐI."
            tab4_cmd = """
            BẮT BUỘC TRẢ VỀ ĐÚNG FORMAT JSON CẨM NANG IN-GAME BÊN TRONG CẶP DẤU ```json VÀ ```.
            ```json
            {
              "individual_instructions": {
                "tan_cong": [{"lenh_duoc_chon": "Defensive", "ap_dung_cho_vi_tri": "DMF"}],
                "phong_ngu": [{"lenh_duoc_chon": "Tight Marking", "ap_dung_cho_vi_tri": "CF"}]
              },
              "k1": "Đội hình xuất phát...", "k2": "Rút thay phòng ngự...", "k3": "Rút thay tấn công..."
            }
            ```
            """
        else:
            tab1_cmd = "CẢNH BÁO TỪ CHỐI."
            tab2_cmd = "CẢNH BÁO TỪ CHỐI."
            tab3_cmd = "SO SÁNH AUTO VS THỦ CÔNG: Chênh lệch chỉ số Tiếng Anh, Hitbox va chạm, và Câu đúc kết giật gân làm Thumbnail Video."
            tab4_cmd = "CẢNH BÁO TỪ CHỐI."

        system_instruction = f"""
        {hard_rules}
        CHIA BÁO CÁO THÀNH 4 PHẦN NGĂN CÁCH NHAU BỞI DẤU "===" NẰM ĐỘC LẬP TRÊN 1 DÒNG.
        PHẦN 1:
        {tab1_cmd}
        ===
        PHẦN 2:
        {tab2_cmd}
        ===
        PHẦN 3:
        {tab3_cmd}
        ===
        PHẦN 4:
        {tab4_cmd}
        """
        
        config = types.GenerateContentConfig(system_instruction=system_instruction, temperature=0.1)
        context_prompt = f"Thông tin: {p_info} | Hệ: {eco} | Chế độ: {mode}"
        contents = [context_prompt] + img_list
        
        client_models = ['gemini-2.5-flash', 'gemini-1.5-flash']
        for m in client_models:
            try:
                response = client.models.generate_content(model=m, contents=contents, config=config)
                if response and response.text: return response.text
            except: continue
            
        return "[LỖI HỆ THỐNG]: Server Google quá tải tạm thời. Vui lòng thử lại!"
    except Exception as e: return f"[LỖI HỆ THỐNG]: {str(e)}"

# ---------------------------------------------------------
# 5. RENDER & FIX LỖI [ 0 : NULL ]
# ---------------------------------------------------------
if st.button("🚀 BẮT ĐẦU PHÂN TÍCH"):
    if not uploaded_players and not uploaded_managers: 
        st.error("Vui lòng tải ít nhất 1 ảnh Cầu thủ hoặc HLV!")
    else:
        with st.spinner("Đang trích xuất Báo cáo Sa bàn..."):
            images_to_send = []
            
            if uploaded_players: 
                for f in uploaded_players: 
                    images_to_send.append(Image.open(f).copy())
            if uploaded_managers: 
                for f in uploaded_managers: 
                    images_to_send.append(Image.open(f).copy())
                    
            st.session_state['raw_report'] = execute_tactical_analysis(images_to_send, player_info, ecosystem, analysis_mode)
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
            <img src="{logo_url}" class="dns-logo-3d">
            <div class="dns-text">{html_content}</div>
            <div class="dns-footer">
                <span style="color: {footer_text_color}; font-style: italic; font-weight: 600;">Đồng bộ lúc: {report_time}</span>
                <span style="color: {label_color}; font-weight: 900;">DNS TACTICAL ARCHITECT</span>
            </div>
        </div>"""

    def extract_json(text):
        try:
            json_match = re.search(r'```json\n([\s\S]*?)\n```', text, re.IGNORECASE)
            if json_match: return json.loads(json_match.group(1).strip())
            match = re.search(r'\{[\s\S]*\}', text)
            if match: return json.loads(match.group(0))
        except: pass
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
                st.markdown(format_tab_content("Đã xảy ra độ trễ truy xuất văn bản AI. Hãy thử bấm phân tích lại (App không bị sập)."), unsafe_allow_html=True)
                
        with t4: 
            if json_data_ingame: st.markdown(format_tab_content(format_in_game_json(json_data_ingame)), unsafe_allow_html=True)
            else: st.markdown(format_tab_content(tab4_c), unsafe_allow_html=True)

    else:
        t1, t2, t4 = st.tabs(["🪪 THẨM ĐỊNH & TRIẾT LÝ", "🛠️ PHÂN BỔ PP", "🎯 CÀI ĐẶT & KỸ NĂNG SA BÀN"])
        with t1: st.markdown(format_tab_content(tab1_c), unsafe_allow_html=True)
        with t2: st.markdown(format_tab_content(tab2_c), unsafe_allow_html=True)
        with t4: st.markdown(format_tab_content(tab4_c), unsafe_allow_html=True)
