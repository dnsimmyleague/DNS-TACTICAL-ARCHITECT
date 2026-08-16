import streamlit as st
from PIL import Image
from google import genai
from google.genai import types
import gc
import re
import datetime

# ---------------------------------------------------------
# 1. CẤU HÌNH TRANG & GIAO DIỆN NỀN TẢNG
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
    
    /* CHỮ MÀU VÀNG - KHÔNG CAN THIỆP HTML */
    .vip-text strong, .expander-content strong, strong {{ color: {label_color} !important; font-weight: 900 !important; }}
    
    .stTabs [data-baseweb="tab-list"] {{ gap: 12px; padding-bottom: 5px; }}
    .stTabs [data-baseweb="tab"] p, .stTabs [data-baseweb="tab"] span {{ color: {tab_inactive_color} !important; font-weight: 700 !important; transition: all 0.3s ease; }}
    .stTabs [data-baseweb="tab"]:hover p {{ color: {text_color} !important; }}
    .stTabs [aria-selected="true"] p, .stTabs [aria-selected="true"] span {{ color: #121418 !important; font-weight: 900 !important; }}
    .stTabs [data-baseweb="tab"] {{ background: {tab_inactive_bg} !important; border: 1px solid {border_color} !important; border-bottom: none !important; border-radius: 14px 14px 0px 0px !important; padding: 12px 18px !important; box-shadow: {shadow_3d} !important; transition: all 0.2s ease-in-out; }}
    .stTabs [data-baseweb="tab"]:hover {{ transform: translateY(-3px); }}
    .stTabs [aria-selected="true"] {{ background: linear-gradient(145deg, #E5C058, #C89B2B) !important; border: 1px solid #F7E08B !important; border-bottom: none !important; transform: translateY(-6px); box-shadow: 0px -6px 15px rgba(200, 155, 43, 0.4) !important; z-index: 10; }}
    
    .vip-card {{ background-color: {element_bg} !important; border: 2px solid {border_color} !important; border-radius: 0px 15px 15px 15px; padding: 25px; box-shadow: {shadow_3d} !important; position: relative; z-index: 2; margin-bottom: 20px; }}
    .vip-logo-3d {{ max-width: 90px; border-radius: 10px; border: 2px solid {border_color}; margin-bottom: 15px; display: block; margin-left: auto; margin-right: auto; }}
    .vip-text {{ font-family: 'Consolas', monospace; font-size: 15px; line-height: 1.7; color: {text_color} !important; }}
    .vip-footer {{ text-align: center; border-top: 1px dashed {border_color}; padding-top: 15px; margin-top: 25px; color: {slogan_color}; font-size: 13px; display: flex; justify-content: space-between; align-items: center; }}
    .warning-box {{ border-left: 5px solid #FF4D4D; background-color: rgba(255,77,77,0.15); padding: 12px 15px; border-radius: 8px; margin-bottom: 12px; color: #FF4D4D !important; font-weight: bold; }}
    
    /* GIAO DIỆN EXPANDER */
    .dns-expander {{ margin-bottom: 12px; border: 1px solid {border_color}; border-radius: 8px; background: {element_bg}; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
    .dns-expander summary {{ padding: 12px 15px; font-weight: 800; color: {label_color}; background: {tab_inactive_bg}; cursor: pointer; list-style: none; font-size: 14.5px; border-bottom: 1px solid transparent; transition: all 0.2s; }}
    .dns-expander summary::-webkit-details-marker {{ display: none; }}
    .dns-expander[open] summary {{ border-bottom: 1px dashed {border_color}; background: linear-gradient(145deg, #2A2F3A, #222730); color: #FFF; }}
    .expander-content {{ padding: 15px; background: {app_bg}; color: {text_color} !important; line-height: 1.6; font-size: 14px; border-top: 1px solid rgba(212, 175, 55, 0.1); }}
    .expander-content ul {{ padding-left: 20px; margin-top: 5px; margin-bottom: 5px; }}
    .expander-content li {{ margin-bottom: 5px; }}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)
st.markdown("<h1 class='title-brand'>DN SIM MY LEAGUE</h1>", unsafe_allow_html=True)
st.markdown("<p class='slogan'>Giải Mã Sơ Đồ - Định Hình Meta - Kiến Tạo Dream Team</p>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. KHỐI NHẬP LIỆU & ĐIỀU HƯỚNG
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
# 3. HÀM RENDER UI THÔNG MINH (DỰA TRÊN MARKDOWN)
# ---------------------------------------------------------
def render_markdown_to_expander(text_block):
    """Biến các gạch đầu dòng cấp 1 thành Hộp Expander"""
    lines = text_block.strip().split('\n')
    html_output = ""
    in_expander = False
    
    for line in lines:
        line_clean = line.strip()
        if not line_clean: continue
        
        # Nhận diện dòng bắt đầu bằng "-" hoặc "*" làm Tiêu đề Expander
        if line_clean.startswith('- **') or line_clean.startswith('* **'):
            if in_expander: html_output += "</div></details>" # Đóng hộp cũ
            
            # Tách tiêu đề và phần còn lại (nếu có trên cùng dòng)
            parts = re.split(r'\*\*(.*?)\*\*(.*)', line_clean[2:])
            if len(parts) >= 3:
                title = parts[1].strip()
                content = parts[2].strip()
            else:
                title = line_clean[2:].replace('**','').strip()
                content = ""
            
            title = title.rstrip(':')
            html_output += f'<details class="dns-expander"><summary>{title}</summary><div class="expander-content">'
            if content:
                content_html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', content.lstrip(':').strip())
                html_output += f"<p>🔹 {content_html}</p>"
            in_expander = True
            
        elif in_expander:
            # Nội dung bên trong Hộp
            content_html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', line_clean)
            if line_clean.startswith('>') or line_clean.startswith('-'):
                html_output += f"<p style='margin-left:15px; margin-bottom:5px;'>🔹 {content_html.lstrip('>').lstrip('-').strip()}</p>"
            else:
                html_output += f"<p style='margin-bottom:5px;'>{content_html}</p>"
        else:
            # Văn bản bình thường không thuộc Hộp nào
            content_html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', line_clean)
            html_output += f"<p>{content_html}</p>"
            
    if in_expander: html_output += "</div></details>"
    return html_output

def clean_text_for_copy(raw_text):
    text = raw_text.replace("===", "\n\n")
    text = re.sub(r'<div class=.*?>', '', text)
    text = text.replace("</div>", "").replace("⛔ ", "")
    text = text.replace("### ", "--- ").replace(" ---", " ---")
    return text.strip()

# ---------------------------------------------------------
# 4. LÕI TƯ DUY AI CHIẾN THUẬT (SYSTEM PROMPT MỚI)
# ---------------------------------------------------------
def execute_tactical_analysis(img_list, p_info, eco, mode):
    try:
        api_key = st.secrets.get("GEMINI_API_KEY")
        if not api_key: return "[LỖI CẤU HÌNH]: Không tìm thấy GEMINI_API_KEY!"
        client = genai.Client(api_key=api_key)
        
        # --- LUẬT THÉP BẤT DI BẤT DỊCH ---
        hard_rules = """
        [LUẬT THÉP - CẤM VI PHẠM DƯỚI MỌI HÌNH THỨC]:
        1. VĂN BẢN TRƠN (MARKDOWN): Chỉ dùng `**chữ**` để in đậm. TUYỆT ĐỐI KHÔNG dùng HTML (Không `<b>`, không `<span>`). KHÔNG gộp dòng. Phải xuống dòng rõ ràng khi chuyển ý.
        2. TÔN TRỌNG GAME: Không dùng từ ngữ đả kích (ngáo, dốt, rác). Bản Auto là "Cân bằng", bản Manual là "Tối ưu".
        3. TỪ ĐIỂN STYLE XANH: Bắt buộc chọn từ (High Line Master, Pass Disruptor, Front Line Pressure, All-action Defender, Covering Role, The Destroyer, Box-to-Box, Defensive GK, Attacking GK, Basic).
        """

        if "1" in mode:
            tab1_cmd = "Thẩm định toàn diện thẻ Auto này với triết lý HLV. Kết luận: Phù hợp (giữ) hay Lệch pha (loại)."
            tab2_cmd = "<div class='warning-box'>⛔ Truy cập bị từ chối: Đang sử dụng thẻ Auto. Tính năng Build PP đã bị vô hiệu hóa.</div>"
            tab3_cmd = "<div class='warning-box'>⛔ Truy cập bị từ chối: Thẻ Auto không hỗ trợ tính năng So sánh mốc điểm thủ công.</div>"
            tab4_cmd = "Xây dựng 3 kịch bản Cài đặt In-game cho vị trí này: Start Game, Tấn công tổng lực, Tử thủ."
        elif "2" in mode:
            tab1_cmd = "Thẩm định chỉ số hiện tại, Style Đỏ/Xanh của thẻ có khớp với sơ đồ HLV không."
            tab2_cmd = "BẮT BUỘC TRA CỨU BẢNG PP: Cấp 4: 4PP | Cấp 5: 6PP | Cấp 6: 8PP | Cấp 7: 10PP | Cấp 8: 12PP | Cấp 9: 15PP | Cấp 10: 18PP | Cấp 11: 21PP | Cấp 12: 24PP. Tính đủ 100% dung lượng thẻ."
            tab3_cmd = "<div class='warning-box'>⛔ Tính năng So sánh đối đầu chuyên sâu được đề xuất sử dụng trong Chế độ 5 (Dự án Video).</div>"
            tab4_cmd = "Xây dựng 3 kịch bản Cài đặt In-game. Đề xuất Top 5 Kỹ năng (Skills)."
        elif "3" in mode:
            tab1_cmd = "Phân tích Sơ đồ Tấn Công (In Possession) và Phòng Ngự (Out of Possession) theo HLV."
            tab2_cmd = "<div class='warning-box'>⛔ Truy cập bị từ chối: Chế độ Khám HLV Tổng quan không bao gồm Quy hoạch Dream Team.</div>"
            tab3_cmd = "<div class='warning-box'>⛔ Truy cập bị từ chối.</div>"
            tab4_cmd = "<div class='warning-box'>⛔ Truy cập bị từ chối.</div>"
        elif "4" in mode:
            tab1_cmd = "Nhận diện triết lý HLV. Trình bày Sơ đồ Tấn công (In Possession) và Sơ đồ Phòng ngự (Out of Possession)."
            tab2_cmd = """
            QUY HOẠCH 23 VỊ TRÍ. 
            LỆNH CẤM RIÊNG CHO PHẦN NÀY: TUYỆT ĐỐI KHÔNG ĐỀ CẬP ĐẾN ĐIỂM PP HAY BẢNG TÍNH PP. KHÔNG NÊU TÊN CẦU THỦ THỰC TẾ.
            
            Bạn BẮT BUỘC phải trình bày ĐÚNG cấu trúc Markdown sau để hệ thống vẽ giao diện:
            
            ### ⚽ HÀNG CÔNG (FW)
            - **CF (Tiền đạo cắm)**: Style Đỏ (Fox In The Box...), Style Xanh (Basic...). Yêu cầu: ...
            - **LWF (Chạy cánh trái)**: Style Đỏ (...), Style Xanh (...). Yêu cầu: ...
            (Tiếp tục liệt kê đủ các vị trí tiền đạo đá chính và dự bị bằng gạch đầu dòng)
            
            ### 🎯 TIỀN VỆ (MF)
            - **AMF (Hộ công)**: ...
            - **CMF (Tiền vệ trung tâm)**: ...
            (Tiếp tục liệt kê đủ các vị trí tiền vệ đá chính và dự bị)
            
            ### 🛡️ HÀNG THỦ (DF)
            - **CB (Trung vệ)**: ...
            (Liệt kê Hậu vệ đá chính và dự bị)
            
            ### 🧤 THỦ MÔN (GK)
            - **GK (Thủ môn)**: ...
            (Liệt kê Thủ môn đá chính và dự bị)
            """
            tab3_cmd = "<div class='warning-box'>⛔ Truy cập bị từ chối: Tab So sánh không áp dụng cho chế độ Quy hoạch Dream Team.</div>"
            tab4_cmd = "Xây dựng 3 kịch bản Cài đặt In-game thay người/lệnh: 1. Start Game. 2. All-out Attack. 3. Park the Bus. LỆNH CẤM: KHÔNG ĐỀ XUẤT KỸ NĂNG (SKILLS) Ở PHẦN NÀY."
        else:
            tab1_cmd = "<div class='warning-box'>⛔ Chế độ Dự án Video: Đang tập trung 100% tài nguyên cho Báo cáo So Sánh.</div>"
            tab2_cmd = "<div class='warning-box'>⛔ Chế độ Dự án Video: Đang tập trung 100% tài nguyên cho Báo cáo So Sánh.</div>"
            tab3_cmd = "SO SÁNH AUTO VS THỦ CÔNG DNS. Quét 100% chỉ số, lập luận việc dịch chuyển điểm từ mốc A sang mốc B để Tối ưu và Phù hợp. Phân tích Manager Boosts. Trình bày rõ ràng: [CHÊNH LỆCH CHỈ SỐ], [LẬP LUẬN CHUYÊN MÔN], [KẾT LUẬN THUMBNAIL]."
            tab4_cmd = "<div class='warning-box'>⛔ Chế độ Dự án Video: Đang tập trung 100% tài nguyên cho Báo cáo So Sánh.</div>"

        system_instruction = f"""
        {hard_rules}
        BẮT BUỘC CHIA BÁO CÁO THÀNH 4 PHẦN NGĂN CÁCH NHAU BỞI DẤU "===" NẰM ĐỘC LẬP TRÊN 1 DÒNG.

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
        response = client.models.generate_content(model='gemini-3.6-flash', contents=contents, config=config)
        return response.text
    except Exception as e:
        return f"[LỖI HỆ THỐNG]: {str(e)}"

# ---------------------------------------------------------
# 5. HIỂN THỊ KẾT QUẢ VÀ RENDER SUB-TABS THÔNG MINH
# ---------------------------------------------------------
if st.button("🚀 BẮT ĐẦU PHÂN TÍCH VIP"):
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
    parts = st.session_state['raw_report'].split("===")
    tab1_c = parts[0].strip() if len(parts)> 0 else "<div class='warning-box'>Lỗi dữ liệu.</div>"
    tab2_c = parts[1].strip() if len(parts) > 1 else "<div class='warning-box'>Lỗi dữ liệu.</div>"
    tab3_c = parts[2].strip() if len(parts) > 2 else "<div class='warning-box'>Lỗi dữ liệu.</div>"
    tab4_c = parts[3].strip() if len(parts) > 3 else "<div class='warning-box'>Lỗi dữ liệu.</div>"
    
    report_time = st.session_state.get('report_time', vn_time_now.strftime("%d/%m/%Y | %H:%M:%S"))
    t1, t2, t3, t4 = st.tabs(["🪪 THẨM ĐỊNH & TRIẾT LÝ", "🛠️ PHÂN BỔ PP & QUY HOẠCH", "⚖️ SO SÁNH AUTO & THỦ CÔNG", "🎯 CÀI ĐẶT & KỸ NĂNG SA BÀN"])
    
    footer_text_color = "#64748B" if is_daytime else "#94A3B8"
    
    def format_tab_content(content):
        # Đổi Markdown in đậm thành HTML <strong> để CSS xử lý màu
        html_content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', content)
        html_content = html_content.replace('\n', '<br>')
        return f"""<div class="vip-card">
            <img src="{logo_url}" class="vip-logo-3d">
            <div class="vip-text">{html_content}</div>
            <div class="vip-footer">
                <span style="color: {footer_text_color}; font-style: italic; font-weight: 600;">Đồng bộ lúc: {report_time}</span>
                <span style="color: {label_color}; font-weight: 900;">DNS TACTICAL ARCHITECT <br> © 2026 DN SIM MY LEAGUE. All rights reserved.</span>
            </div>
        </div>"""

    with t1: 
        if "warning-box" in tab1_c: st.markdown(tab1_c, unsafe_allow_html=True)
        else: st.markdown(format_tab_content(tab1_c), unsafe_allow_html=True)
    
    with t2: 
        if "warning-box" in tab2_c: 
            st.markdown(tab2_c, unsafe_allow_html=True)
        elif "### ⚽ HÀNG CÔNG" in tab2_c:
            # XỬ LÝ CHIA 4 SUB-TABS THÔNG MINH DỰA TRÊN MARKDOWN HEADER
            sections = re.split(r'### ', tab2_c)
            intro = sections[0].strip()
            
            fw_content = mf_content = df_content = gk_content = ""
            for sec in sections[1:]:
                if sec.startswith("⚽"): fw_content = sec
                elif sec.startswith("🎯"): mf_content = sec
                elif sec.startswith("🛡️"): df_content = sec
                elif sec.startswith("🧤"): gk_content = sec
            
            if intro:
                st.markdown(f"""<div class="vip-card" style="margin-bottom: 10px; padding-bottom: 15px;">
                    <img src="{logo_url}" class="vip-logo-3d">
                    <div class="vip-text">{re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', intro).replace(chr(10), '<br>')}</div>
                </div>""", unsafe_allow_html=True)
            
            s1, s2, s3, s4 = st.tabs(["⚽ HÀNG CÔNG (FW)", "🎯 TIỀN VỆ (MF)", "🛡️ HÀNG THỦ (DF)", "🧤 THỦ MÔN (GK)"])
            with s1: 
                if fw_content: st.markdown(render_markdown_to_expander(fw_content), unsafe_allow_html=True)
            with s2:
                if mf_content: st.markdown(render_markdown_to_expander(mf_content), unsafe_allow_html=True)
            with s3:
                if df_content: st.markdown(render_markdown_to_expander(df_content), unsafe_allow_html=True)
            with s4:
                if gk_content: st.markdown(render_markdown_to_expander(gk_content), unsafe_allow_html=True)
            
            st.markdown(f"""<div class="vip-card" style="margin-top: 10px; padding: 15px;">
                <div class="vip-footer" style="margin-top: 0; padding-top:0; border:none;">
                    <span style="color: {footer_text_color}; font-style: italic; font-weight: 600;">Đồng bộ lúc: {report_time}</span>
                    <span style="color: {label_color}; font-weight: 900;">DNS TACTICAL ARCHITECT <br> © 2026 DN SIM MY LEAGUE. All rights reserved.</span>
                </div>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(format_tab_content(tab2_c), unsafe_allow_html=True)
            
    with t3: 
        if "warning-box" in tab3_c: st.markdown(tab3_c, unsafe_allow_html=True)
        else: st.markdown(format_tab_content(tab3_c), unsafe_allow_html=True)
        
    with t4: 
        if "warning-box" in tab4_c: st.markdown(tab4_c, unsafe_allow_html=True)
        else: st.markdown(format_tab_content(tab4_c), unsafe_allow_html=True)
    
    with st.expander("Bấm vào đây để Copy văn bản thô (Dành cho Team Content)"):
        clean_raw = clean_text_for_copy(st.session_state['raw_report'])
        st.text_area("Văn bản gốc (Markdown sạch):", value=clean_raw, height=250)
