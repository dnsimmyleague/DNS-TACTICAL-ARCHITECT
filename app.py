import streamlit as st
from PIL import Image
from google import genai
from google.genai import types
import gc
import re
import datetime

# ---------------------------------------------------------
# 1. CẤU HÌNH TRANG & GIAO DIỆN NỀN TẢNG (HỆ KIM VIP)
# ---------------------------------------------------------
st.set_page_config(page_title="DN SIM MY LEAGUE | VIP DNS", page_icon="👑", layout="centered")

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
    tab_inactive_bg = "linear-gradient(145deg, #F8FAFC, #E2E8F0)"
    tab_inactive_color = "#111827"  # CHỐT: Màu chữ Đen Đậm siêu rõ ban ngày
    watermark_opacity = "0.04"; watermark_blend = "multiply"
    expander_copy_bg = "#F8FAFC"
    subtab_bg = "linear-gradient(145deg, #f0f0f0, #cacaca)"
    subtab_shadow = "5px 5px 10px #bebebe, -5px -5px 10px #ffffff"
    subtab_active_bg = "linear-gradient(145deg, #D4AF37, #B8860B)"
    subtab_active_shadow = "inset 5px 5px 10px #9a7009, inset -5px -5px 10px #fceea5"
else:
    app_bg = "#1E222A"; element_bg = "#252A34"; text_color = "#F1F5F9"
    label_color = "#E5C058"; slogan_color = "#94A3B8"; border_color = "#D4AF37"
    shadow_3d = "6px 6px 14px rgba(0,0,0,0.35), -4px -4px 10px rgba(255,255,255,0.03)"
    tab_inactive_bg = "linear-gradient(145deg, #252A34, #1E222A)"
    tab_inactive_color = "#F3F4F6"  # CHỐT: Màu Trắng Bạc siêu rõ ban đêm
    watermark_opacity = "0.08"; watermark_blend = "screen"
    expander_copy_bg = "#1A1D24"
    subtab_bg = "linear-gradient(145deg, #21252e, #1c1f26)"
    subtab_shadow = "5px 5px 10px #15181d, -5px -5px 10px #2d323f"
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
        color: {label_color} !important; font-weight: 800 !important; font-size: 16px !important;
        background-color: transparent !important; text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
    }}
    
    [data-testid="stExpander"] {{ background-color: {expander_copy_bg} !important; border-radius: 8px; border: 1px solid {border_color}; margin-top: 15px; }}
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
    
    .vip-text strong, .expander-content strong, strong {{ color: {label_color} !important; font-weight: 900 !important; }}
    
    /* FIX TAB CHÍNH: Hiện rõ chữ, Đổ bóng nổi khối 3D */
    .stTabs [data-baseweb="tab-list"] {{ gap: 12px; padding-bottom: 5px; }}
    .stTabs [data-baseweb="tab"] p, .stTabs [data-baseweb="tab"] span {{ color: {tab_inactive_color} !important; font-weight: 800 !important; transition: all 0.3s ease; }}
    .stTabs [data-baseweb="tab"]:hover p {{ color: {label_color} !important; }}
    .stTabs [aria-selected="true"] p, .stTabs [aria-selected="true"] span {{ color: #121418 !important; font-weight: 900 !important; }}
    .stTabs [data-baseweb="tab"] {{ background: {tab_inactive_bg} !important; border: 1.5px solid rgba(212, 175, 55, 0.4) !important; border-bottom: none !important; border-radius: 14px 14px 0px 0px !important; padding: 12px 18px !important; box-shadow: {shadow_3d} !important; transition: all 0.2s ease-in-out; }}
    .stTabs [data-baseweb="tab"]:hover {{ transform: translateY(-3px); border-color: {border_color} !important; }}
    .stTabs [aria-selected="true"] {{ background: linear-gradient(145deg, #E5C058, #C89B2B) !important; border: 1px solid #F7E08B !important; border-bottom: none !important; transform: translateY(-6px); box-shadow: 0px -6px 15px rgba(200, 155, 43, 0.4) !important; z-index: 10; }}
    
    div[data-testid="stTabs"] div[data-testid="stTabs"] [data-baseweb="tab-list"] {{ display: flex; justify-content: space-between; background: transparent; padding: 10px 0; border: none; }}
    div[data-testid="stTabs"] div[data-testid="stTabs"] [data-baseweb="tab"] {{
        flex: 1; margin: 0 5px; border-radius: 12px !important; padding: 15px 5px !important; text-align: center;
        background: {subtab_bg} !important;
        box-shadow: {subtab_shadow} !important;
        border: 1px solid rgba(212, 175, 55, 0.2) !important;
        transition: all 0.3s ease; transform: none;
    }}
    div[data-testid="stTabs"] div[data-testid="stTabs"] [data-baseweb="tab"] p {{ color: {text_color} !important; font-size: 14px !important; font-weight: 800 !important; }}
    div[data-testid="stTabs"] div[data-testid="stTabs"] [aria-selected="true"] {{
        background: {subtab_active_bg} !important;
        box-shadow: {subtab_active_shadow} !important;
        border: 1px solid {border_color} !important;
    }}
    div[data-testid="stTabs"] div[data-testid="stTabs"] [aria-selected="true"] p {{ color: #121418 !important; }}

    .vip-card {{ background-color: {element_bg} !important; border: 2px solid {border_color} !important; border-radius: 0px 15px 15px 15px; padding: 25px; box-shadow: {shadow_3d} !important; position: relative; z-index: 2; margin-bottom: 20px; }}
    .vip-logo-3d {{ max-width: 90px; border-radius: 10px; border: 2px solid {border_color}; margin-bottom: 15px; display: block; margin-left: auto; margin-right: auto; }}
    .vip-text {{ font-family: 'Consolas', monospace; font-size: 15px; line-height: 1.7; color: {text_color} !important; }}
    .vip-footer {{ text-align: center; border-top: 1px dashed {border_color}; padding-top: 15px; margin-top: 25px; color: {slogan_color}; font-size: 13px; display: flex; justify-content: space-between; align-items: center; }}
    .warning-box {{ border-left: 5px solid #FF4D4D; background-color: rgba(255,77,77,0.15); padding: 12px 15px; border-radius: 8px; margin-bottom: 12px; color: #FF4D4D !important; font-weight: bold; }}
    
    .dns-expander {{ margin-bottom: 12px; margin-top: 10px; border-radius: 10px; background: {element_bg}; overflow: hidden; box-shadow: {subtab_shadow}; border: 1px solid rgba(212, 175, 55, 0.3); }}
    .dns-expander summary {{ padding: 15px; font-weight: 800; color: {label_color}; background: {subtab_bg}; cursor: pointer; list-style: none; font-size: 14.5px; transition: all 0.2s; }}
    .dns-expander summary::-webkit-details-marker {{ display: none; }}
    .dns-expander[open] summary {{ border-bottom: 1px dashed {border_color}; background: {subtab_active_bg}; color: #121418 !important; box-shadow: {subtab_active_shadow}; }}
    .expander-content {{ padding: 15px; background: {app_bg}; color: {text_color} !important; line-height: 1.6; font-size: 14px; border-top: 1px solid rgba(212, 175, 55, 0.1); }}
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
# 3. HÀM XỬ LÝ TEXT VÀ RENDER SUB-TABS TỰ ĐỘNG (BẢN CHỐT LỖI)
# ---------------------------------------------------------
def render_expander_from_list(items):
    if not items: return "<p style='color: #64748B; font-style: italic;'>Không có dữ liệu cho tuyến này.</p>"
    html_out = ""
    for item in items:
        # Bóc tách Tên vị trí và Nội dung
        match = re.match(r'^[\d\.\-\*]*\s*([A-Z/]+[\s\w\(\)]*?):\s*(.*)', item.strip())
        if match:
            title = match.group(1).strip().replace('**', '')
            content = match.group(2).strip()
            content_html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', content)
            html_out += f'<details class="dns-expander"><summary>{title}</summary><div class="expander-content"><p>🔹 {content_html}</p></div></details>'
        else:
            # Fallback nếu không tách được dấu hai chấm
            title = item.split('(')[0].replace('**', '').replace('-', '').strip()
            content_html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', item.replace(title, '', 1).strip())
            if not title: title = "Phân tích vị trí"
            html_out += f'<details class="dns-expander"><summary>{title}</summary><div class="expander-content"><p>🔹 {content_html}</p></div></details>'
    return html_out

def parse_and_group_positions(text_block):
    """Tự động gom cầu thủ vào đúng 4 Tuyến bất chấp AI viết lung tung"""
    fw_list, mf_list, df_list, gk_list = [], [], [], []
    # Dọn dẹp câu chữ PP lọt lưới
    text_block = re.sub(r'\(Cấp \d+\s*-\s*\d+PP\)', '', text_block)
    
    # Cắt văn bản theo từng gạch đầu dòng hoặc đánh số (1., 2., -, *)
    lines = re.split(r'\n(?=[\d\-\*]+\.?\s*[A-Z]{2})', text_block.strip())
    
    for line in lines:
        line_clean = line.strip().replace('\n', ' ')
        if not line_clean: continue
        
        # Nhận diện vị trí để nhét vào rổ
        # FW: CF, ST, SS, LWF, RWF
        if re.search(r'\b(CF|ST|SS|LWF|RWF)\b', line_clean.split(':')[0]):
            fw_list.append(line_clean)
        # MF: AMF, CMF, DMF, LMF, RMF
        elif re.search(r'\b(AMF|CMF|DMF|LMF|RMF)\b', line_clean.split(':')[0]):
            mf_list.append(line_clean)
        # DF: CB, LB, RB, LWB, RWB
        elif re.search(r'\b(CB|LB|RB|LWB|RWB)\b', line_clean.split(':')[0]):
            df_list.append(line_clean)
        # GK: GK
        elif re.search(r'\b(GK)\b', line_clean.split(':')[0]):
            gk_list.append(line_clean)
            
    return fw_list, mf_list, df_list, gk_list

def clean_text_for_copy(raw_text, mode):
    if mode.startswith("4"):
        parts = raw_text.split("===")
        if len(parts) >= 4:
            raw_text = f"{parts[0]}\n\n{parts[1]}\n\n{parts[3]}"
    
    text = raw_text.replace("===", "\n\n").replace("⛔ ", "")
    text = re.sub(r'\*\*', '', text) # Dọn sạch sành sanh dấu sao
    text = re.sub(r'\(Cấp \d+\s*-\s*\d+PP\)', '', text) # Xóa nốt PP trong bản copy
    text = text.replace("CẢNH BÁO TỪ CHỐI.", "").replace("CẢNH BÁO TỪ CHỐI DO ĐANG DÙNG THẺ AUTO.", "").replace("CẢNH BÁO TỪ CHỐI DÀNH CHO DỰ ÁN VIDEO.", "").replace("CẢNH BÁO TỪ CHỐI DÀNH CHO BUILD 23 NGƯỜI.", "")
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

# ---------------------------------------------------------
# 4. LÕI TƯ DUY AI
# ---------------------------------------------------------
def execute_tactical_analysis(img_list, p_info, eco, mode):
    try:
        api_key = st.secrets.get("GEMINI_API_KEY")
        if not api_key: return "[LỖI CẤU HÌNH]: Không tìm thấy GEMINI_API_KEY!"
        client = genai.Client(api_key=api_key)
        
        hard_rules = """
        [QUY TẮC BẮT BUỘC]:
        1. Tuyệt đối không dùng HTML. Chỉ dùng `**chữ**` để in đậm.
        2. Chỉ chọn (High Line Master, Pass Disruptor, Front Line Pressure, All-action Defender, Covering Role, The Destroyer, Box-to-Box, Defensive GK, Attacking GK, Basic).
        """

        if "1" in mode:
            tab1_cmd = "Thẩm định thẻ Auto này với triết lý HLV."
            tab2_cmd = "CẢNH BÁO TỪ CHỐI DO ĐANG DÙNG THẺ AUTO."
            tab3_cmd = "CẢNH BÁO TỪ CHỐI DO ĐANG DÙNG THẺ AUTO."
            tab4_cmd = "3 kịch bản Cài đặt In-game: Start Game, Tấn công tổng lực, Tử thủ."
        elif "2" in mode:
            tab1_cmd = "Thẩm định chỉ số, Style Đỏ/Xanh."
            tab2_cmd = "TRA CỨU BẢNG PP: Cấp 4: 4PP... Tính 100% dung lượng thẻ."
            tab3_cmd = "CẢNH BÁO TỪ CHỐI DÀNH CHO DỰ ÁN VIDEO."
            tab4_cmd = "3 kịch bản Cài đặt In-game. Đề xuất Top 5 Skills bổ sung."
        elif "3" in mode:
            tab1_cmd = "Phân tích Sơ đồ Tấn Công và Phòng Ngự."
            tab2_cmd = "CẢNH BÁO TỪ CHỐI DÀNH CHO BUILD 23 NGƯỜI."
            tab3_cmd = "CẢNH BÁO TỪ CHỐI."
            tab4_cmd = "CẢNH BÁO TỪ CHỐI."
        elif "4" in mode:
            tab1_cmd = "Phân tích Triết lý HLV. Vẽ Sơ đồ Tấn công và Sơ đồ Phòng ngự."
            tab2_cmd = """
            QUY HOẠCH ĐỦ 23 VỊ TRÍ ĐÁ CHÍNH VÀ DỰ BỊ DỰA TRÊN SƠ ĐỒ Ở PHẦN 1.
            [LỆNH CẤM THÉP]: KHÔNG VIẾT TỪ 'PP' HAY 'CẤP'. KHÔNG ĐỀ XUẤT ĐIỂM SỐ. KHÔNG NÊU TÊN CẦU THỦ THỰC TẾ.
            Bắt buộc liệt kê danh sách theo cú pháp:
            - **[Tên Vị Trí]**: Style Đỏ (...), Style Xanh (...). Yêu cầu: ...
            
            Ví dụ:
            - **CF**: Front Line Pressure. Chạy chỗ cắt mặt.
            - **LWF**: Creative Playmaker. Rê dắt và tạt bóng.
            (Kê khai đủ 23 người).
            """
            tab3_cmd = "CẢNH BÁO TỪ CHỐI."
            tab4_cmd = """
            3 kịch bản Cài đặt In-game:
            1. Start Game: Cài đặt lệnh ...
            2. Tăng 1/2 nấc Đỏ (Tấn công): Cài đặt lệnh ...
            3. Hạ 1/2 nấc Xanh (Phòng ngự): Cài đặt lệnh ...
            [LỆNH CẤM THÉP]: KHÔNG ĐƯỢC ĐỀ XUẤT THÊM SKILLS KỸ NĂNG NÀO Ở ĐÂY.
            """
        else:
            tab1_cmd = "CẢNH BÁO TỪ CHỐI DÀNH CHO DỰ ÁN VIDEO."
            tab2_cmd = "CẢNH BÁO TỪ CHỐI DÀNH CHO DỰ ÁN VIDEO."
            tab3_cmd = "SO SÁNH AUTO VS MANUAL DNS. Lập luận phân tích [CHÊNH LỆCH CHỈ SỐ], [LẬP LUẬN CHUYÊN MÔN]."
            tab4_cmd = "CẢNH BÁO TỪ CHỐI DÀNH CHO DỰ ÁN VIDEO."

        system_instruction = f"""
        {hard_rules}
        CHIA BÁO CÁO THÀNH 4 PHẦN NGĂN CÁCH BỞI DẤU "===" NẰM ĐỘC LẬP TRÊN 1 DÒNG.

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
        response = client.models.generate_content(model='gemini-3.6-flash', contents=contents, config=config)
        return response.text
    except Exception as e:
        return f"[LỖI HỆ THỐNG]: {str(e)}"

# ---------------------------------------------------------
# 5. RENDER GIAO DIỆN
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
    
    # BỘ LỌC CỨNG BẰNG PYTHON (LOẠI BỎ SẠCH PP & SKILLS LÉN LÚT Ở CHẾ ĐỘ 4)
    if mode_selected == "4":
        lines_2 = st.session_state['raw_report'].split("===")
        if len(lines_2) > 1:
            clean_tab2 = re.sub(r'\(?Cấp \d+\s*-\s*\d+PP\)?', '', lines_2[1]) # Chém PP
            lines_2[1] = clean_tab2
            st.session_state['raw_report'] = "===".join(lines_2)
            
        lines_4 = st.session_state['raw_report'].split("===")
        if len(lines_4) > 3:
            clean_tab4 = lines_4[3].split("Top 5")[0].split("TOP 5")[0].split("Skills")[0] # Chém Skills
            lines_4[3] = clean_tab4
            st.session_state['raw_report'] = "===".join(lines_4)
            
    parts = st.session_state['raw_report'].split("===")
    tab1_c = parts[0].strip() if len(parts) > 0 else ""
    tab2_c = parts[1].strip() if len(parts) > 1 else ""
    tab3_c = parts[2].strip() if len(parts) > 2 else ""
    tab4_c = parts[3].strip() if len(parts) > 3 else ""
    
    report_time = st.session_state.get('report_time', vn_time_now.strftime("%d/%m/%Y | %H:%M:%S"))
    footer_text_color = "#64748B" if is_daytime else "#94A3B8"
    
    def format_tab_content(content):
        if "CẢNH BÁO TỪ CHỐI" in content:
            return f"<div class='warning-box'>⛔ Tính năng này đã bị khóa do không thuộc phạm vi của Chế độ phân tích hiện tại.</div>"
        # Xóa sạch ký tự rác ở đuôi
        content_clean = re.sub(r'(\d+\.|\*+)\s*$', '', content.strip())
        html_content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', content_clean).replace('\n', '<br>')
        return f"""<div class="vip-card">
            <img src="{logo_url}" class="vip-logo-3d">
            <div class="vip-text">{html_content}</div>
            <div class="vip-footer">
                <span style="color: {footer_text_color}; font-style: italic; font-weight: 600;">Đồng bộ lúc: {report_time}</span>
                <span style="color: {label_color}; font-weight: 900;">DNS TACTICAL ARCHITECT <br> © 2026 DN SIM MY LEAGUE. All rights reserved.</span>
            </div>
        </div>"""

    if mode_selected == "1":
        t1, t4 = st.tabs(["🪪 THẨM ĐỊNH & TRIẾT LÝ", "🎯 CÀI ĐẶT & KỸ NĂNG SA BÀN"])
        with t1: st.markdown(format_tab_content(tab1_c), unsafe_allow_html=True)
        with t4: st.markdown(format_tab_content(tab4_c), unsafe_allow_html=True)
        
    elif mode_selected == "2":
        t1, t2, t4 = st.tabs(["🪪 THẨM ĐỊNH & TRIẾT LÝ", "🛠️ PHÂN BỔ PP", "🎯 CÀI ĐẶT & KỸ NĂNG SA BÀN"])
        with t1: st.markdown(format_tab_content(tab1_c), unsafe_allow_html=True)
        with t2: st.markdown(format_tab_content(tab2_c), unsafe_allow_html=True)
        with t4: st.markdown(format_tab_content(tab4_c), unsafe_allow_html=True)
        
    elif mode_selected == "3":
        t1 = st.tabs(["🪪 THẨM ĐỊNH & TRIẾT LÝ"])[0]
        with t1: st.markdown(format_tab_content(tab1_c), unsafe_allow_html=True)
        
    elif mode_selected == "4":
        t1, t2, t4 = st.tabs(["🪪 THẨM ĐỊNH & TRIẾT LÝ", "🛠️ QUY HOẠCH 23 CẦU THỦ", "🎯 CÀI ĐẶT & KỸ NĂNG SA BÀN"])
        with t1: st.markdown(format_tab_content(tab1_c), unsafe_allow_html=True)
        
        with t2: 
            # DÙNG PYTHON GOM TỰ ĐỘNG VÀO 4 TAB 3D BẤT CHẤP AI VIẾT GÌ
            fw_list, mf_list, df_list, gk_list = parse_and_group_positions(tab2_c)
            
            # Nếu Python nhặt được cầu thủ, vẽ 4 khối 3D. Nếu không, in bình thường.
            if fw_list or mf_list or df_list or gk_list:
                s1, s2, s3, s4 = st.tabs(["⚽ FW", "🎯 MF", "🛡️ DF", "🧤 GK"])
                with s1: st.markdown(render_expander_from_list(fw_list), unsafe_allow_html=True)
                with s2: st.markdown(render_expander_from_list(mf_list), unsafe_allow_html=True)
                with s3: st.markdown(render_expander_from_list(df_list), unsafe_allow_html=True)
                with s4: st.markdown(render_expander_from_list(gk_list), unsafe_allow_html=True)
                
                st.markdown(f"""<div class="vip-card" style="margin-top: 10px; padding: 15px;">
                    <div class="vip-footer" style="margin-top: 0; padding-top:0; border:none;">
                        <span style="color: {footer_text_color}; font-style: italic; font-weight: 600;">Đồng bộ lúc: {report_time}</span>
                        <span style="color: {label_color}; font-weight: 900;">DNS TACTICAL ARCHITECT <br> © 2026 DN SIM MY LEAGUE. All rights reserved.</span>
                    </div>
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown(format_tab_content(tab2_c), unsafe_allow_html=True)
                
        with t4: 
            st.markdown(format_tab_content(tab4_c), unsafe_allow_html=True)
        
    elif mode_selected == "5":
        t3 = st.tabs(["⚖️ SO SÁNH AUTO & THỦ CÔNG"])[0]
        with t3: st.markdown(format_tab_content(tab3_c), unsafe_allow_html=True)
    
    with st.expander("Bấm vào đây để Copy văn bản thô (Dành cho Team Content)"):
        clean_raw = clean_text_for_copy(st.session_state['raw_report'], mode_selected)
        st.text_area("Văn bản gốc (Markdown sạch):", value=clean_raw, height=250)
