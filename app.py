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
    tab_inactive_color = "#0F172A"  # [CHỐT FIX] Màu Đen Đậm Cực Nét
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
    tab_inactive_bg = "linear-gradient(145deg, #252A34, #1E222A)"
    tab_inactive_color = "#F8FAFC"  # [CHỐT FIX] Màu Trắng Bạc Cực Nét
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
    
    /* SPINNER TRONG SUỐT HOÀN TOÀN, CHỮ VÀNG KIM */
    div[data-testid="stSpinner"] {{ background-color: transparent !important; }}
    div[data-testid="stSpinner"] svg circle {{ stroke: {border_color} !important; }}
    div[data-testid="stSpinner"] > div > span, div[data-testid="stSpinner"] p {{
        color: {label_color} !important; font-weight: 900 !important; font-size: 17px !important;
        background-color: transparent !important; text-shadow: 1px 1px 3px rgba(0,0,0,0.5);
    }}
    
    /* KHUNG COPY VĂN BẢN MÀU NỀN ĐỘC LẬP */
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
    
    .vip-text strong, .expander-content strong, strong {{ color: {label_color} !important; font-weight: 900 !important; }}
    
    /* [CƯỠNG CHẾ CẤP CAO] BẮT TẤT CẢ TỰA TAB CÓ MÀU ĐEN RÕ BAN NGÀY / TRẮNG BAN ĐÊM */
    .stTabs [data-baseweb="tab-list"] {{ gap: 12px; padding-bottom: 5px; }}
    button[data-baseweb="tab"] * {{
        color: {tab_inactive_color} !important;
        font-weight: 800 !important;
        transition: all 0.3s ease;
    }}
    button[data-baseweb="tab"]:hover * {{
        color: {label_color} !important;
    }}
    button[data-baseweb="tab"][aria-selected="true"] * {{
        color: #121418 !important;
        font-weight: 900 !important;
    }}
    .stTabs [data-baseweb="tab"] {{
        background: {tab_inactive_bg} !important;
        border: 1.5px solid {border_color} !important;
        border-bottom: none !important;
        border-radius: 14px 14px 0px 0px !important;
        padding: 12px 18px !important;
        box-shadow: {shadow_3d} !important;
        transition: all 0.2s ease-in-out;
    }}
    .stTabs [aria-selected="true"] {{
        background: linear-gradient(145deg, #E5C058, #C89B2B) !important;
        border: 1.5px solid #F7E08B !important;
        border-bottom: none !important;
        transform: translateY(-6px);
        box-shadow: 0px -6px 15px rgba(200, 155, 43, 0.4) !important;
        z-index: 10;
    }}
    
    /* SUB-TABS 3D TRONG TAB 2 (MỞ RỘNG VÀ ĐỔ BÓNG NỔI KHỐI) */
    div[data-testid="stTabs"] div[data-testid="stTabs"] [data-baseweb="tab-list"] {{ display: flex; justify-content: space-between; background: transparent; padding: 15px 0; border: none; }}
    div[data-testid="stTabs"] div[data-testid="stTabs"] button[data-baseweb="tab"] {{
        flex: 1; margin: 0 6px; border-radius: 12px !important; padding: 14px 8px !important; text-align: center;
        background: {subtab_bg} !important;
        box-shadow: {subtab_shadow} !important;
        border: 1.5px solid rgba(212, 175, 55, 0.3) !important;
        transition: all 0.3s ease; transform: none;
    }}
    div[data-testid="stTabs"] div[data-testid="stTabs"] button[data-baseweb="tab"] * {{
        color: {text_color} !important;
        font-size: 15px !important;
        font-weight: 900 !important;
    }}
    div[data-testid="stTabs"] div[data-testid="stTabs"] button[aria-selected="true"] {{
        background: {subtab_active_bg} !important;
        box-shadow: {subtab_active_shadow} !important;
        border: 1.5px solid {border_color} !important;
    }}
    div[data-testid="stTabs"] div[data-testid="stTabs"] button[aria-selected="true"] * {{
        color: #121418 !important;
    }}

    .vip-card {{ background-color: {element_bg} !important; border: 2px solid {border_color} !important; border-radius: 0px 15px 15px 15px; padding: 25px; box-shadow: {shadow_3d} !important; position: relative; z-index: 2; margin-bottom: 20px; }}
    .vip-logo-3d {{ max-width: 90px; border-radius: 10px; border: 2px solid {border_color}; margin-bottom: 15px; display: block; margin-left: auto; margin-right: auto; }}
    .vip-text {{ font-family: 'Consolas', monospace; font-size: 15px; line-height: 1.7; color: {text_color} !important; }}
    .vip-footer {{ text-align: center; border-top: 1px dashed {border_color}; padding-top: 15px; margin-top: 25px; color: {slogan_color}; font-size: 13px; display: flex; justify-content: space-between; align-items: center; }}
    .warning-box {{ border-left: 5px solid #FF4D4D; background-color: rgba(255,77,77,0.15); padding: 12px 15px; border-radius: 8px; margin-bottom: 12px; color: #FF4D4D !important; font-weight: bold; }}
    
    .dns-expander {{ margin-bottom: 12px; margin-top: 10px; border-radius: 10px; background: {element_bg}; overflow: hidden; box-shadow: {subtab_shadow}; border: 1px solid rgba(212, 175, 55, 0.3); }}
    .dns-expander summary {{ padding: 15px; font-weight: 800; color: {label_color}; background: {subtab_bg}; cursor: pointer; list-style: none; font-size: 15px; transition: all 0.2s; }}
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
# 3. HÀM XỬ LÝ VÀ PHÂN LOẠI DANH SÁCH 23 CẦU THỦ THÔNG MINH
# ---------------------------------------------------------
def render_expander_from_list(items):
    if not items: 
        return "<p style='color: #64748B; font-style: italic; text-align: center; padding: 20px;'>Không có vị trí phù hợp cho tuyến này.</p>"
    
    html_out = ""
    for item in items:
        item_clean = re.sub(r'^[\d\.\-\*]+\s*', '', item).strip()
        if not item_clean: continue
        
        if ':' in item_clean:
            title, content = item_clean.split(':', 1)
        else:
            title = "Phân tích vị trí"
            content = item_clean
            
        title = title.replace('*', '').strip()
        content_clean = content.replace('*', '').strip()
        
        # Kiểm tra nếu nội dung bị rỗng thì không hiển thị bẫy rỗng
        if not content_clean or len(content_clean) < 2:
            continue
            
        content_html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', content)
        content_html = content_html.replace('*', '').strip()
        
        html_out += f'<details class="dns-expander"><summary>{title}</summary><div class="expander-content"><p>🔹 {content_html}</p></div></details>'
    return html_out

def parse_and_group_positions(text_block):
    """Phân loại chính xác 23 vị trí vào 4 Tuyến 3D"""
    fw_list, mf_list, df_list, gk_list = [], [], [], []
    intro_text = ""
    
    # Hủy diệt sạch văn bản rác PP / Bảng quy đổi trước khi chia
    text_block = re.sub(r'Bảng quy đổi.*?HLV:', '', text_block, flags=re.IGNORECASE | re.DOTALL)
    text_block = re.sub(r'Quy hoạch phân bổ PP.*?:', '', text_block, flags=re.IGNORECASE)
    text_block = re.sub(r'\(?Cấp \d+.*?\d*PP\)?', '', text_block, flags=re.IGNORECASE)
    text_block = re.sub(r'\d+%\s*PP', '', text_block, flags=re.IGNORECASE)
    text_block = re.sub(r'\(Khai thác 100% dung lượng thẻ\)', '', text_block, flags=re.IGNORECASE)
    
    lines = text_block.split('\n')
    
    for line in lines:
        line_clean = line.strip()
        if not line_clean or line_clean.startswith('#'): continue
        
        # Bỏ qua các dòng gạch ngang rác
        if line_clean in ['-', '*', '--', '---']: continue
        
        parts = line_clean.split(':')
        header_part = parts[0].upper()
        
        if re.search(r'\b(CF|ST|SS|LWF|RWF|RW|LW|HÀNG CÔNG)\b', header_part): 
            fw_list.append(line_clean)
        elif re.search(r'\b(AMF|CMF|DMF|LMF|RMF|RM|LM|TIỀN VỆ)\b', header_part): 
            mf_list.append(line_clean)
        elif re.search(r'\b(CB|LB|RB|LWB|RWB|HẬU VỆ|HÀNG THỦ)\b', header_part): 
            df_list.append(line_clean)
        elif re.search(r'\b(GK|THỦ MÔN)\b', header_part): 
            gk_list.append(line_clean)
        else:
            if not any(lst for lst in [fw_list, mf_list, df_list, gk_list]):
                if "PP" not in line_clean and "CẤP" not in line_clean.upper():
                    intro_text += line_clean + "<br>"
                
    return intro_text.strip(), fw_list, mf_list, df_list, gk_list

def clean_text_for_copy(raw_text, mode):
    if mode.startswith("4"):
        parts = raw_text.split("===")
        if len(parts) >= 4:
            raw_text = f"{parts[0]}\n\n{parts[1]}\n\n{parts[3]}"
    
    text = raw_text.replace("===", "\n\n").replace("⛔ ", "")
    text = text.replace("*", "") 
    text = re.sub(r'\(?Cấp \d+.*?\d*PP\)?', '', text, flags=re.IGNORECASE) 
    text = re.sub(r'Bảng quy đổi.*?HLV:', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\d+\.\s*Đề\s*xuất.*', '', text, flags=re.IGNORECASE)
    text = text.replace("CẢNH BÁO TỪ CHỐI.", "").replace("CẢNH BÁO TỪ CHỐI DO ĐANG DÙNG THẺ AUTO.", "").replace("CẢNH BÁO TỪ CHỐI DÀNH CHO DỰ ÁN VIDEO.", "").replace("CẢNH BÁO TỪ CHỐI DÀNH CHO BUILD 23 NGƯỜI.", "")
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

# ---------------------------------------------------------
# 4. LÕI TƯ DUY AI CHIẾN THUẬT BẬC THẦY (CHUẨN 23 CẦU THỦ)
# ---------------------------------------------------------
def execute_tactical_analysis(img_list, p_info, eco, mode):
    try:
        api_key = st.secrets.get("GEMINI_API_KEY")
        if not api_key: return "[LỖI CẤU HÌNH]: Không tìm thấy GEMINI_API_KEY!"
        client = genai.Client(api_key=api_key)
        
        hard_rules = """
        [QUY TẮC BẮT BUỘC]:
        1. Tuyệt đối không dùng HTML. Chỉ dùng `**chữ**` để in đậm.
        2. Tôn trọng Style Cơ bản In-game gốc (Goal Poacher, Build Up, Anchor Man, Orchestrator...). Style Xanh chỉ là lớp bọc lót bổ trợ.
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
            QUY HOẠCH ĐỦ 23 VỊ TRÍ (11 ĐÁ CHÍNH + 12 DỰ BỊ) DỰA TRÊN SƠ ĐỒ VÀ TRIẾT LÝ Ở PHẦN 1.
            [LỆNH CẤM THÉP]: TUYỆT ĐỐI KHÔNG VIẾT TỪ 'PP', 'CẤP', KHÔNG TÍNH TOÁN % ĐIỂM SỐ. KHÔNG BỎ TRỐNG NỘI DUNG.
            
            YÊU CẦU ĐỊNH DẠNG (BẮT BUỘC ĐỀ XUẤT CẦU THỦ THỰC TẾ TIÊU BIỂU):
            Mỗi vị trí trình bày trên 1 dòng duy nhất theo đúng cấu trúc mẫu sau:
            - **[Tên Vị Trí]**: Đá chính: **[Tên Cầu thủ thực tế]** ([Style Cơ bản In-game gốc] + [Style Xanh bổ trợ nếu có]) — Dự bị: **[Tên Cầu thủ dự bị]** ([Style Cơ bản]). Vai trò: [Giải thích ngắn gọn tư duy vận hành].
            
            VÍ DỤ MẪU BẮT BUỘC THEO:
            - **CF (Tiền đạo cắm)**: Đá chính: **Erling Haaland** (Goal Poacher + Front Line Pressure) — Dự bị: **Victor Osimhen** (Goal Poacher). Vai trò: Săn bàn chủ lực, đè mặt trung vệ dứt điểm 1 chạm.
            - **CB (Lệch trái)**: Đá chính: **Virgil van Dijk** (Build Up + High Line Master) — Dự bị: **Alessandro Nesta** (Build Up). Vai trò: Thắt chặt cự ly, bọc lót không gian sau lưng.
            - **DMF (Tiền vệ phòng ngự)**: Đá chính: **Rodri** (Anchor Man + Pass Disruptor) — Dự bị: **Casemiro** (The Destroyer). Vai trò: Đánh chặn trung lộ và thu hồi bóng.
            
            LƯU Ý: Phải kê khai ĐỦ 23 CẦU THỦ chia đều cho 4 tuyến (FW: 5-6, MF: 6-7, DF: 7-8, GK: 2-3).
            """
            tab3_cmd = "CẢNH BÁO TỪ CHỐI."
            tab4_cmd = """
            CẨM NANG IN-GAME VÀ KỊCH BẢN THAY NGƯỜI CHIẾN THUẬT:
            
            1. Gán Lệnh Cá Nhân (Individual Instructions):
            - Tấn công (Max 2 slot): CHỈ ĐƯỢC CHỌN 'Defensive' hoặc 'Anchoring'. Gán cho vị trí nào?
            - Phòng ngự (Max 2 slot): CHỈ ĐƯỢC CHỌN 'Tight Marking', 'Man Marking', hoặc 'Counter Target'. Gán cho vị trí nào?
            
            2. Kịch Bản Thay Người & Chỉnh Nấc Mental Level:
            - Kịch bản 1 (Start Game - Cân bằng): Giữ cự ly đội hình.
            - Kịch bản 2 (Đang dẫn bàn - Hạ 1/2 nấc Xanh): Rút vị trí nào ra, đưa ai vào (Thay bổ sung cầu thủ phòng ngự).
            - Kịch bản 3 (Bị dẫn bàn - Tăng 1/2 nấc Đỏ): Rút vị trí nào ra, đưa ai vào (Thay bổ sung tiền đạo càn lướt).
            
            [LỆNH CẤM TUYỆT ĐỐI]: KHÔNG ĐƯỢC ĐỀ XUẤT THÊM BẤT KỲ KỸ NĂNG SKILLS NÀO Ở ĐÂY.
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
        response = client.models.generate_content(model='gemini-3.6-flash', contents=contents, config=config)
        return response.text
    except Exception as e:
        return f"[LỖI HỆ THỐNG]: {str(e)}"

# ---------------------------------------------------------
# 5. RENDER GIAO DIỆN & BỘ LỌC TỐI CAO
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
    
    # [LỌC CỨNG] DIỆT SẠCH PP VÀ SKILLS CHẾ ĐỘ 4
    if mode_selected == "4":
        lines_2 = st.session_state['raw_report'].split("===")
        if len(lines_2) > 1:
            clean_tab2 = re.sub(r'\(?Cấp \d+.*?\d*PP\)?', '', lines_2[1], flags=re.IGNORECASE)
            clean_tab2 = re.sub(r'\d+%\s*PP', '', clean_tab2, flags=re.IGNORECASE)
            clean_tab2 = re.sub(r'Bảng quy đổi.*?HLV:', '', clean_tab2, flags=re.IGNORECASE)
            lines_2[1] = clean_tab2
            st.session_state['raw_report'] = "===".join(lines_2)
            
        lines_4 = st.session_state['raw_report'].split("===")
        if len(lines_4) > 3:
            clean_tab4 = lines_4[3].split("Top 5")[0].split("TOP 5")[0].split("Skills")[0].split("Kỹ năng")[0]
            clean_tab4 = re.sub(r'\d+\.\s*Đề\s*xuất.*', '', clean_tab4, flags=re.IGNORECASE)
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
        
        html_content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', content)
        html_content = html_content.replace('*', '').replace('\n', '<br>')
        
        return f"""<div class="vip-card">
            <img src="{logo_url}" class="vip-logo-3d">
            <div class="vip-text">{html_content}</div>
            <div class="vip-footer">
                <span style="color: {footer_text_color}; font-style: italic; font-weight: 600;">Đồng bộ lúc: {report_time}</span>
                <span style="color: {label_color}; font-weight: 900;">DNS TACTICAL ARCHITECT <br> © 2026 DN SIM MY LEAGUE. All rights reserved.</span>
            </div>
        </div>"""

    # ĐIỀU HƯỚNG TAB
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
            intro_text, fw_list, mf_list, df_list, gk_list = parse_and_group_positions(tab2_c)
            
            if fw_list or mf_list or df_list or gk_list:
                if intro_text and len(intro_text) > 10:
                    intro_html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', intro_text).replace('*', '')
                    st.markdown(f"""<div class="vip-card" style="margin-bottom: 10px; padding-bottom: 15px;">
                        <img src="{logo_url}" class="vip-logo-3d">
                        <div class="vip-text">{intro_html}</div>
                    </div>""", unsafe_allow_html=True)
                
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
