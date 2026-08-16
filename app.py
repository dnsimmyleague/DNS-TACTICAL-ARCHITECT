import streamlit as st
from PIL import Image
from google import genai
from google.genai import types
import gc
import re
import datetime

# ---------------------------------------------------------
# 1. CẤU HÌNH TRANG & THEME THÔNG MINH
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

# ---------------------------------------------------------
# 2. CSS VÀ GIAO DIỆN VIP NỀN TẢNG
# ---------------------------------------------------------
logo_url = "https://i.postimg.cc/4KNSdqRd/D9754823-56B4-4957-8F90-1EE072CFF5A2.jpg"

if is_daytime:
    app_bg = "#F4F6F9"; element_bg = "#FFFFFF"; text_color = "#1E293B"
    label_color = "#D4AF37"; slogan_color = "#64748B"; border_color = "#D4AF37"
    shadow_3d = "6px 6px 14px rgba(0,0,0,0.06), -6px -6px 14px rgba(255,255,255,0.9)"
    tab_inactive_bg = "linear-gradient(145deg, #FFFFFF, #E2E8F0)"; tab_inactive_color = "#374151"
    watermark_opacity = "0.04"; watermark_blend = "multiply"
else:
    app_bg = "#1E222A"; element_bg = "#252A34"; text_color = "#F1F5F9"
    label_color = "#E5C058"; slogan_color = "#94A3B8"; border_color = "#D4AF37"
    shadow_3d = "6px 6px 14px rgba(0,0,0,0.35), -4px -4px 10px rgba(255,255,255,0.03)"
    tab_inactive_bg = "linear-gradient(145deg, #252A34, #1E222A)"; tab_inactive_color = "#9CA3AF"
    watermark_opacity = "0.08"; watermark_blend = "screen"

st.markdown(f"""<div class="watermark-logo"></div>""", unsafe_allow_html=True)

custom_css = f"""
<style>
    header[data-testid="stHeader"] {{ display: none !important; }} footer {{ display: none !important; }}
    .stApp {{ background-color: {app_bg} !important; transition: background-color 0.4s ease; }}
    .watermark-logo {{
        position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%);
        width: 450px; height: 450px; background-image: url('{logo_url}');
        background-size: cover; background-repeat: no-repeat; background-position: center;
        opacity: {watermark_opacity}; mix-blend-mode: {watermark_blend}; pointer-events: none; z-index: 0;
        border-radius: 50%; -webkit-mask-image: radial-gradient(circle closest-side, black 65%, transparent 100%);
        mask-image: radial-gradient(circle closest-side, black 65%, transparent 100%);
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
    [data-testid="stSpinner"] svg circle {{ stroke: {border_color} !important; }}
    [data-testid="stSpinner"] p, [data-testid="stSpinner"] span {{ color: {border_color} !important; font-weight: 900 !important; font-size: 17px !important; }}
    .stTabs [data-baseweb="tab-list"] {{ gap: 12px; padding-bottom: 5px; }}
    .stTabs [data-baseweb="tab"] p, .stTabs [data-baseweb="tab"] span {{ color: {tab_inactive_color} !important; font-weight: 700 !important; transition: all 0.3s ease; }}
    .stTabs [data-baseweb="tab"]:hover p {{ color: {text_color} !important; }}
    .stTabs [aria-selected="true"] p, .stTabs [aria-selected="true"] span {{ color: #121418 !important; font-weight: 900 !important; }}
    .stTabs [data-baseweb="tab"] {{ background: {tab_inactive_bg} !important; border: 1px solid {border_color} !important; border-bottom: none !important; border-radius: 14px 14px 0px 0px !important; padding: 12px 18px !important; box-shadow: {shadow_3d} !important; transition: all 0.2s ease-in-out; }}
    .stTabs [data-baseweb="tab"]:hover {{ transform: translateY(-3px); }}
    .stTabs [aria-selected="true"] {{ background: linear-gradient(145deg, #E5C058, #C89B2B) !important; border: 1px solid #F7E08B !important; border-bottom: none !important; transform: translateY(-6px); box-shadow: 0px -6px 15px rgba(200, 155, 43, 0.4) !important; z-index: 10; }}
    .vip-card {{ background-color: {element_bg} !important; border: 2px solid {border_color} !important; border-radius: 0px 15px 15px 15px; padding: 25px; box-shadow: {shadow_3d} !important; position: relative; z-index: 2; }}
    .vip-logo-3d {{ max-width: 90px; border-radius: 10px; border: 2px solid {border_color}; transition: transform 0.3s ease; }}
    .vip-logo-3d:hover {{ transform: scale(1.05) rotate(1deg); }}
    .vip-text {{ font-family: 'Consolas', monospace; font-size: 15px; line-height: 1.6; white-space: pre-wrap; color: {text_color} !important; }}
    .vip-footer {{ text-align: center; border-top: 1px dashed {border_color}; padding-top: 15px; margin-top: 20px; color: {slogan_color}; font-size: 13px; display: flex; justify-content: space-between; align-items: center; }}
    .warning-box {{ border-left: 5px solid #FF4D4D; background-color: rgba(255,77,77,0.15); padding: 12px 15px; border-radius: 8px; margin-bottom: 12px; color: #FF4D4D !important; font-weight: bold; }}
    /* EXPANDER UI CHO 23 CẦU THỦ */
    .dns-expander {{ margin-bottom: 12px; border: 1px solid {border_color}; border-radius: 8px; background: {element_bg}; box-shadow: {shadow_3d}; }}
    .dns-expander summary {{ padding: 12px 15px; font-weight: 900; color: {label_color}; background: {tab_inactive_bg}; cursor: pointer; border-radius: 8px; list-style: none; font-family: 'Consolas', monospace; font-size: 15px; }}
    .dns-expander summary::-webkit-details-marker {{ display: none; }}
    .dns-expander[open] summary {{ border-bottom-left-radius: 0; border-bottom-right-radius: 0; border-bottom: 1px dashed {border_color}; }}
    .expander-content {{ padding: 15px; background: {app_bg}; border-bottom-left-radius: 8px; border-bottom-right-radius: 8px; color: {text_color} !important; line-height: 1.6; font-family: 'Consolas', monospace; font-size: 14px; }}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)
st.markdown("<h1 class='title-brand'>DN SIM MY LEAGUE</h1>", unsafe_allow_html=True)
st.markdown("<p class='slogan'>Giải Mã Sơ Đồ - Định Hình Meta - Kiến Tạo Dream Team</p>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. KHỐI NHẬP LIỆU & ĐIỀU HƯỚNG 5 KỊCH BẢN TÙY BIẾN
# ---------------------------------------------------------
analysis_mode = st.radio(
    "🎯 CHỌN CHẾ ĐỘ PHÂN TÍCH (TỰ ĐỘNG ĐÓNG/MỞ TAB):",
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
# 4. LÕI TƯ DUY AI (TỐI ƯU HÓA HOÀN TOÀN)
# ---------------------------------------------------------
def clean_text_and_build_ui(raw_text):
    # Dọn dẹp lỗi HTML rác có thể phát sinh từ AI
    text = raw_text.replace("<b>", "**").replace("</b>", "**").replace("</b", "**")
    text = text.replace("$", "").replace("#", "")
    text = text.replace("\\rightarrow", "->").replace("\\Rightarrow", "=>")
    
    # Dịch mã Tag BOX thành Giao diện Expander UI
    def box_replacer(match):
        title = match.group(1).strip()
        content = match.group(2).strip()
        content = re.sub(r'\*\*(.*?)\*\*', r'<b style="color:#D4AF37">\1</b>', content)
        content = content.replace('\n', '<br>')
        return f'<details class="dns-expander"><summary>{title}</summary><div class="expander-content">{content}</div></details>'
    
    text = re.sub(r'\[BOX:\s*(.*?)\](.*?)\[/BOX\]', box_replacer, text, flags=re.DOTALL)
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    text = text.replace("> ", "🔹 ")
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text

def execute_tactical_analysis(img_list, p_info, eco, mode):
    try:
        api_key = st.secrets.get("GEMINI_API_KEY")
        if not api_key: return "[LỖI CẤU HÌNH]: Không tìm thấy GEMINI_API_KEY!"
        client = genai.Client(api_key=api_key)
        
        # KIẾN TRÚC LỆNH TÙY BIẾN THEO MODE CHỌN VÀ KHÓA TAB
        if "1" in mode:
            tab1_cmd = "Thẩm định độ tương thích của thẻ Auto này với lối chơi HLV. Hợp thì khuyên dùng, lệch pha thì loại thẳng tay."
            tab2_cmd = "<div class='warning-box'>⛔ Truy cập bị từ chối: Boss đang dùng thẻ Auto (Khóa chỉ số). Tính năng Build PP đã bị vô hiệu hóa.</div>"
            tab3_cmd = "<div class='warning-box'>⛔ Truy cập bị từ chối: Thẻ Auto không thể So sánh mốc thủ công.</div>"
            tab4_cmd = "🎯 Viết 3 kịch bản Cài đặt In-game: Start Game, Tấn công tổng lực, Tử thủ bảo vệ tỷ số cho riêng cầu thủ này."
        elif "2" in mode:
            tab1_cmd = "Thẩm định chỉ số hiện tại, Hitbox và Style Đỏ/Xanh của thẻ có khớp với HLV không."
            tab2_cmd = """🔹 BẮT BUỘC TRA CỨU BẢNG PP: [Cấp 4 tốn 4 PP | Cấp 5 tốn 6 PP | Cấp 6 tốn 8 PP | Cấp 7 tốn 10 PP | Cấp 8 tốn 12 PP | Cấp 9 tốn 15 PP | Cấp 10 tốn 18 PP | Cấp 11 tốn 21 PP | Cấp 12 tốn 24 PP]. Tính tổng 100% dung lượng thẻ, đề xuất nâng cấp bù đắp những điểm yếu."""
            tab3_cmd = "<div class='warning-box'>⛔ Tính năng này hiện tại được khuyên dùng trong Chế độ Dự án Video So Sánh.</div>"
            tab4_cmd = "🎯 Viết 3 kịch bản Cài đặt In-game: Start Game, Tấn công tổng lực, Tử thủ bảo vệ tỷ số. Top 5 kỹ năng (Skills) đề xuất."
        elif "3" in mode:
            tab1_cmd = "Phân tích Sơ đồ Tấn Công (In Possession) và Phòng Ngự (Out of Possession) dựa vào triết lý của HLV."
            tab2_cmd = "<div class='warning-box'>⛔ Truy cập bị từ chối: Chế độ Khám HLV Tổng quan không bao gồm Quy hoạch Dream Team.</div>"
            tab3_cmd = "<div class='warning-box'>⛔ Truy cập bị từ chối.</div>"
            tab4_cmd = "<div class='warning-box'>⛔ Truy cập bị từ chối.</div>"
        elif "4" in mode:
            tab1_cmd = "Nhận diện Triết lý HLV. Vẽ ra 2 Sơ đồ: Tấn Công và Phòng Ngự."
            tab2_cmd = """🔹 QUY HOẠCH 23 NHÂN SỰ TỐI ƯU. BẮT BUỘC DÙNG CÚ PHÁP TAG [BOX] ĐỂ RENDER UI:
            **🟢 ĐỘI HÌNH ĐÁ CHÍNH (11 Vị trí)**
            **⚽ HÀNG CÔNG (FW)**
            [BOX: CF - Tiền đạo cắm]
            - **Style Đỏ 🔴**: ...
            - **Style Xanh 🔵**: ... (Mặc định Basic nếu không yêu cầu đặc thù)
            - **Vai trò**: ...
            [/BOX]
            (Làm tương tự bọc [BOX] cho MF, DF, GK và 12 cầu thủ Dự Bị) CẤM GỌI TÊN CẦU THỦ CỤ THỂ!"""
            tab3_cmd = "<div class='warning-box'>⛔ Truy cập bị từ chối: Tab So sánh không dùng cho chế độ Dream Team.</div>"
            tab4_cmd = "🎯 Dựa trên 11 vị trí xuất phát, viết 3 kịch bản Cài đặt In-game thay người/khóa lệnh: 1. Mặc định Start Game. 2. All-out Attack (Bị dẫn bàn). 3. Park the Bus (Tử thủ bảo vệ tỷ số)."
        else: # Mode 5: Dự án Video So sánh
            tab1_cmd = "<div class='warning-box'>⛔ Chế độ Dự án Video: Đang tập trung 100% tài nguyên cho Báo cáo So Sánh.</div>"
            tab2_cmd = "<div class='warning-box'>⛔ Chế độ Dự án Video: Đang tập trung 100% tài nguyên cho Báo cáo So Sánh.</div>"
            tab3_cmd = """🔹 CHẾ ĐỘ CHUYÊN GIA DỮ LIỆU. Quét 100% chỉ số ảnh So sánh (Auto vs Manual DNS). 
            - Lập luận cực sắc bén: Vì sao Manual DNS giảm điểm mục A để tăng mục B (Tối ưu cho vai trò/Style gì).
            - Cộng dồn Buff HLV vào để thấy sự thay đổi.
            - Bố cục: [CHÊNH LỆCH CHỈ SỐ], [LẬP LUẬN CHUYÊN MÔN], [KẾT LUẬN THUMBNAIL] để dọn cỗ cho Team Content."""
            tab4_cmd = "<div class='warning-box'>⛔ Chế độ Dự án Video: Đang tập trung 100% tài nguyên cho Báo cáo So Sánh.</div>"

        system_instruction = f"""
        Bạn là DNS TACTICAL ARCHITECT - Chuyên gia Data & Chiến thuật eFootball.
        
        🚫 VĂN HÓA NGÔN TỪ (CẤM VI PHẠM):
        - CẤM dùng từ ngữ đả kích, chê bai (như: ngáo, dốt, rác, ngu ngốc, vô dụng...).
        - LUÔN tôn trọng bản Auto là bản build Cân bằng của Konami. Bản Manual DNS là sự tinh chỉnh để "TỐI ƯU" và "PHÙ HỢP" nhất với sa bàn chuyên sâu. Hãy giữ thái độ chuyên nghiệp, sắc bén.

        🚫 KỶ LUẬT ĐỊNH DẠNG & LOGIC:
        - KHÔNG dùng HTML `<b>`, `</b`. Chỉ dùng Markdown `**`.
        - HITBOX: Chỉ nhắc đến Sải chân/Va chạm khi nó thực sự là chìa khóa chiến thuật sống còn của vị trí đó. KHÔNG lạm dụng.
        - STYLE XANH BẮT BUỘC: Nếu đề xuất, chỉ được dùng (High Line Master, Pass Disruptor, Front Line Pressure, All-action Defender, Covering Role, The Destroyer, Box-to-Box, Defensive GK, Attacking GK). Nếu không cần, dùng `Basic`.
        - CÁCH TRÌNH BÀY STYLE XANH: Bắt buộc in đậm 🔵 **[TÊN STYLE]** và giải thích cơ chế lùi khối CỦA NÓ NGAY TRÊN CÙNG 1 DÒNG (Tuyệt đối không được ngắt dòng).

        BẮT BUỘC CHIA BÁO CÁO THÀNH 4 PHẦN NGĂN CÁCH BỞI "===" TRÊN 1 DÒNG RIÊNG (Nếu có lệnh in Cảnh báo ⛔, CHỈ in đúng cảnh báo đó, không giải thích thêm).

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
        context_prompt = f"Thông tin: {p_info} | Hệ: {eco} | Chế độ đang chọn: {mode}"
        
        contents = [context_prompt] + img_list
        response = client.models.generate_content(model='gemini-1.5-flash', contents=contents, config=config)
        return clean_text_and_build_ui(response.text)
    except Exception as e:
        return f"[LỖI HỆ THỐNG]: {str(e)}"

# ---------------------------------------------------------
# 5. RENDER 4 TABS KẾT QUẢ ĐẦY ĐỦ
# ---------------------------------------------------------
if st.button("🚀 BẮT ĐẦU PHÂN TÍCH VIP"):
    if not uploaded_players and not uploaded_managers: 
        st.error("Vui lòng tải ít nhất 1 ảnh Cầu thủ hoặc HLV để tiến hành phân tích!")
    else:
        with st.spinner("Hệ thống đang trích xuất Báo cáo Sa bàn theo chế độ đã chọn..."):
            images_to_send = []
            if uploaded_players:
                for f in uploaded_players: images_to_send.append(Image.open(f).copy())
            if uploaded_managers:
                for f in uploaded_managers: images_to_send.append(Image.open(f).copy())
                
            st.session_state['analysis_report'] = execute_tactical_analysis(images_to_send, player_info, ecosystem, analysis_mode)
            st.session_state['report_time'] = vn_time_now.strftime("%d/%m/%Y | %H:%M:%S")
            images_to_send.clear(); gc.collect()

if 'analysis_report' in st.session_state:
    parts = st.session_state['analysis_report'].split("===")
    tab1_c = parts[0] if len(parts) > 0 else "<div class='warning-box'>Lỗi dữ liệu.</div>"
    tab2_c = parts[1] if len(parts) > 1 else "<div class='warning-box'>Lỗi dữ liệu.</div>"
    tab3_c = parts[2] if len(parts) > 2 else "<div class='warning-box'>Lỗi dữ liệu.</div>"
    tab4_c = parts[3] if len(parts) > 3 else "<div class='warning-box'>Lỗi dữ liệu.</div>"
    
    report_time = st.session_state.get('report_time', vn_time_now.strftime("%d/%m/%Y | %H:%M:%S"))
    t1, t2, t3, t4 = st.tabs(["🪪 THẨM ĐỊNH & TRIẾT LÝ", "🛠️ PHÂN BỔ PP & QUY HOẠCH", "⚖️ SO SÁNH AUTO & THỦ CÔNG", "🎯 CÀI ĐẶT & KỸ NĂNG SA BÀN"])
    
    footer_text_color = "#64748B" if is_daytime else "#94A3B8"
    
    def format_tab(content):
        return f"""<div class="vip-card">
            <div style="text-align:center; margin-bottom: 18px;"><img src="{logo_url}" class="vip-logo-3d"></div>
            <div class="vip-text">{content.strip()}</div>
            <div class="vip-footer">
                <span style="color: {footer_text_color}; font-style: italic; font-weight: 600;">Đồng bộ lúc: {report_time}</span>
                <span style="color: {label_color}; font-weight: 900; text-shadow: 0px 1px 2px rgba(184, 134, 11, 0.4);">DNS TACTICAL ARCHITECT <br> © 2026 DN SIM MY LEAGUE.</span>
            </div>
        </div>"""

    with t1: st.markdown(format_tab(tab1_c), unsafe_allow_html=True)
    with t2: st.markdown(format_tab(tab2_c), unsafe_allow_html=True)
    with t3: st.markdown(format_tab(tab3_c), unsafe_allow_html=True)
    with t4: st.markdown(format_tab(tab4_c), unsafe_allow_html=True)
    
    with st.expander("Bấm vào đây để Copy văn bản thô (Dành cho Team Content)"):
        # Trích xuất văn bản phẳng để copy
        raw_text = st.session_state['analysis_report'].replace("<b>", "").replace("</b>", "").replace("<div class='warning-box'>", "").replace("</div>", "").replace("===", "\n\n")
        raw_text = re.sub(r'<b style="color:#D4AF37">', '', raw_text)
        raw_text = re.sub(r'<details.*?>', '', raw_text); raw_text = re.sub(r'</details>', '', raw_text)
        raw_text = re.sub(r'<summary.*?>', '[', raw_text); raw_text = re.sub(r'</summary>', ']\n', raw_text)
        raw_text = re.sub(r'<div class="expander-content">', '', raw_text)
        st.text_area("Văn bản gốc:", value=raw_text.replace('<br>', '\n').replace('⛔ ', ''), height=200)
