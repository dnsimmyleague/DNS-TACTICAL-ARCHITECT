import streamlit as st
from PIL import Image
from google import genai
from google.genai import types
import gc
import re
import datetime

# ---------------------------------------------------------
# 1. CẤU HÌNH TRANG & NÚT GẠT THEME GÓC PHẢI
# ---------------------------------------------------------
st.set_page_config(page_title="DN SIM MY LEAGUE | VIP DNS", page_icon="👑", layout="centered")

vn_time_now = datetime.datetime.utcnow() + datetime.timedelta(hours=7)
default_is_daytime = 6 <= vn_time_now.hour < 18

if 'manual_theme' not in st.session_state:
    st.session_state['manual_theme'] = "Ban Ngày ☀️" if default_is_daytime else "Ban Đêm 🌙"

selected_theme = st.radio(
    "Theme Switcher",
    ["Ban Ngày ☀️", "Ban Đêm 🌙"],
    index=0 if st.session_state['manual_theme'] == "Ban Ngày ☀️" else 1,
    horizontal=True,
    label_visibility="collapsed"
)
st.session_state['manual_theme'] = selected_theme
is_daytime = (st.session_state['manual_theme'] == "Ban Ngày ☀️")

# ---------------------------------------------------------
# 2. HỆ MÀU MỆNH KIM & CHÈN LOGO ĐỘC LẬP
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

    label, .stCheckbox > label > div > p {{ color: {label_color} !important; font-weight: bold !important; font-size: 15px !important; }}
    .stTextInput > div > div > input, .stSelectbox > div > div > div, .stSelectbox > div > div > [role="combobox"] {{
        background-color: {element_bg} !important; color: {text_color} !important;
        font-weight: 600 !important; border-radius: 12px !important; border: 1px solid {border_color} !important; box-shadow: {shadow_3d} !important; padding: 12px !important;
    }}
    ul[data-baseweb="menu"] {{ background-color: {element_bg} !important; border: 1px solid {border_color} !important; }}
    ul[data-baseweb="menu"] li {{ color: {text_color} !important; }}

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
    
    /* GIAO DIỆN EXPANDER 23 CẦU THỦ */
    .dns-expander {{ margin-bottom: 12px; border: 1px solid {border_color}; border-radius: 8px; background: {element_bg}; box-shadow: {shadow_3d}; }}
    .dns-expander summary {{ padding: 12px 15px; font-weight: 900; color: {label_color}; background: {tab_inactive_bg}; cursor: pointer; border-radius: 8px; list-style: none; font-family: 'Consolas', monospace; font-size: 15px; }}
    .dns-expander summary::-webkit-details-marker {{ display: none; }}
    .dns-expander[open] summary {{ border-bottom-left-radius: 0; border-bottom-right-radius: 0; border-bottom: 1px dashed {border_color}; }}
    .expander-content {{ padding: 15px; background: {app_bg}; border-bottom-left-radius: 8px; border-bottom-right-radius: 8px; color: {text_color} !important; line-height: 1.6; font-family: 'Consolas', monospace; font-size: 14px; }}
    .expander-content b {{ color: {label_color} !important; }}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)
st.markdown("<h1 class='title-brand'>DN SIM MY LEAGUE</h1>", unsafe_allow_html=True)
st.markdown("<p class='slogan'>Giải Mã Sơ Đồ - Định Hình Meta - Kiến Tạo Dream Team</p>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. KHỐI NHẬP LIỆU GIAO DIỆN
# ---------------------------------------------------------
player_info = st.text_input("👤 Tên Cầu thủ/Sơ đồ (Bỏ trống nếu không cần):", placeholder="Ví dụ: Roberto Carlos, Frank Lampard hoặc 4-2-1-3")
ecosystem = st.selectbox("🌐 Chọn hệ sinh thái (SIM AI / PvP):", ["SIM AI", "PvP"], index=1)
is_comparison = st.checkbox("✅ ĐÂY LÀ ẢNH SO SÁNH CẦU THỦ (Trái: AUTO | Phải: THỦ CÔNG DNS)")

st.markdown("<p style='color: #D4AF37; font-weight: 900; margin-bottom: 0px;'>📸 1. Tải ảnh Cầu thủ (eFHUB và Ảnh Dual Styles in-game):</p>", unsafe_allow_html=True)
uploaded_players = st.file_uploader("Quét chọn nhiều ảnh cùng lúc", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True, key="player_imgs")

st.markdown("<p style='color: #D4AF37; font-weight: 900; margin-bottom: 0px; margin-top: 15px;'>📸 2. Tải ảnh HLV (Link-up / Manager Buff):</p>", unsafe_allow_html=True)
uploaded_managers = st.file_uploader("Quét chọn nhiều ảnh HLV", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True, key="manager_imgs")

# ---------------------------------------------------------
# 4. LÕI TƯ DUY AI (VŨ KHÍ TỐI THƯỢNG ĐÃ ĐƯỢC MÀI GIŨA)
# ---------------------------------------------------------
def clean_text_and_build_ui(raw_text):
    # Dọn dẹp lỗi HTML rác do AI có thể sinh ra nhầm
    text = raw_text.replace("<b>", "**").replace("</b>", "**").replace("</b", "**")
    text = text.replace("$", "").replace("#", "")
    text = text.replace("\\rightarrow", "->").replace("\\Rightarrow", "=>")
    
    if "🚨" in text or "⚠️" in text:
        text = f"<div class='warning-box'>{text}</div>"

    # THUẬT TOÁN BUILD GIAO DIỆN 23 CẦU THỦ TỪ TAG [BOX]
    def box_replacer(match):
        title = match.group(1).strip()
        content = match.group(2).strip()
        # Parse Markdown sang HTML bên trong hộp Expander
        content = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', content)
        content = content.replace('\n', '<br>')
        return f'<details class="dns-expander"><summary>{title}</summary><div class="expander-content">{content}</div></details>'
    
    text = re.sub(r'\[BOX:\s*(.*?)\](.*?)\[/BOX\]', box_replacer, text, flags=re.DOTALL)
    
    # Xử lý in đậm chuẩn ngoài các Box
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    text = text.replace("> ", "🔹 ")
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text

def execute_tactical_analysis(img_list, p_info, eco, is_comp, is_only_manager):
    try:
        api_key = st.secrets.get("GEMINI_API_KEY")
        if not api_key: return "[LỖI CẤU HÌNH]: Không tìm thấy GEMINI_API_KEY!"
            
        client = genai.Client(api_key=api_key)
        
        system_instruction = f"""
        Bạn là DNS TACTICAL ARCHITECT - Chuyên gia Phân tích Chiến thuật eFootball Cấp Cao.
        
        KỊCH BẢN HIỆN TẠI: {"[CHỈ CÓ ẢNH HLV - ĐỊNH HÌNH SA BÀN & QUY HOẠCH ĐỘI HÌNH]" if is_only_manager else "[CÓ ẢNH CẦU THỦ - THẨM ĐỊNH TƯƠNG THÍCH & NÂNG CẤP]"}
        
        🚫 KỶ LUẬT TƯ DUY & ĐỊNH DẠNG TỐI THƯỢNG (CẤM VI PHẠM):
        1. TUYỆT ĐỐI KHÔNG dùng các thẻ HTML như `<b>`, `</b>`, `</b`. Chỉ dùng cú pháp Markdown `**chữ cần in đậm**`.
        2. TƯ DUY XỬ LÝ HITBOX/THÔNG SỐ: Đừng nhai lại từ "Hitbox" máy móc. Chỉ phân tích thông số Sải chân/Va chạm khi nó thực sự là chìa khóa sống còn cho vị trí đó, nếu không thì bỏ qua để tập trung vào vận hành sa bàn.
        3. STYLE XANH: Nếu ảnh có Style Xanh, BẮT BUỘC HIGHLIGHT (VD: 🔵 **TÊN STYLE XANH**) và phân tích cơ chế lùi khối/cắt bóng CỦA NÓ NGAY TRÊN CÙNG 1 DÒNG (Tuyệt đối không được ngắt dòng).
        4. QUY HOẠCH ĐỘI HÌNH: CẤM NÊU TÊN CẦU THỦ CỤ THỂ. Chỉ được nêu Vai trò, Style Đỏ, Style Xanh và Chỉ số.
        5. ĐỊNH DẠNG: Viết liền mạch, KHÔNG xuống dòng vô lý. Bắt buộc chia 4 phần bằng đúng 3 dấu "===" nằm trên 1 dòng riêng biệt.

        === NẾU LÀ KỊCH BẢN CHỈ CÓ ẢNH HLV ===
        PHẦN 1: ĐỌC VỊ TRIẾT LÝ & VẬN HÀNH KÉP (Trước === thứ 1)
        🔹 Nhận diện Triết lý HLV.
        🔹 Phân tích Sơ đồ Kép: 
           - Sơ đồ Tấn công (In Possession): Đội hình dâng lên thành sơ đồ gì?
           - Sơ đồ Phòng ngự (Out of Possession): Lùi khối tạo thành sơ đồ gì?
        
        ===
        PHẦN 2: PHÂN BỔ PP & QUY HOẠCH (Giữa === 1 và 2)
        🔹 QUY HOẠCH 23 NHÂN SỰ TỐI ƯU.
        🔹 ĐỂ TẠO GIAO DIỆN EXPANDER CHO NGƯỜI DÙNG, BẠN BẮT BUỘC PHẢI DÙNG CÚ PHÁP TAG [BOX] SAU ĐÂY CHO ĐÚNG 23 VỊ TRÍ:
        
        **🟢 ĐỘI HÌNH ĐÁ CHÍNH (11 Vị trí)**
        **⚽ HÀNG CÔNG (FW)**
        [BOX: CF - Tiền đạo cắm]
        - **Style Đỏ 🔴**: ...
        - **Style Xanh 🔵**: ... (Mặc định Basic nếu không cần đặc thù)
        - **Vai trò cốt lõi**: ...
        [/BOX]
        (Làm tương tự cho LWF, RWF...)
        
        **🎯 TUYẾN TIỀN VỆ (MF)**
        (Làm tương tự bọc trong [BOX]...[/BOX] cho AMF, CMF...)
        
        **🛡️ HÀNG PHÒNG NGỰ (DF)**
        (Làm tương tự bọc trong [BOX]...[/BOX] cho CB, LB...)
        
        **🧤 THỦ MÔN (GK)**
        (Làm tương tự bọc trong [BOX]...[/BOX])
        
        **🟡 DỰ BỊ CHIẾN THUẬT (12 Vị trí)**
        (Làm tương tự chia theo Tuyến và bọc trong [BOX]...[/BOX] cho 12 cầu thủ xoay tua)
        
        ===
        PHẦN 3: VẬN HÀNH BÀI ĐÁNH THỰC CHIẾN (Giữa === 2 và 3)
        🔹 Triển khai bóng.
        🔹 Phương án khoét nách & kết liễu.
        🔹 Tổ chức lùi khối sa bàn.
        
        ===
        PHẦN 4: CÀI ĐẶT SA BÀN & INSIGHT STREAM (Sau === thứ 3)
        🎯 Individual Instructions (để trám khoảng trống).
        🎙️ Insight Chốt Hạ.

        === NẾU LÀ KỊCH BẢN CÓ ẢNH CẦU THỦ ===
        PHẦN 1: THẨM ĐỊNH TOÀN DIỆN & TRIẾT LÝ (Trước === thứ 1)
        🔹 ĐỌC 100% TỪ ẢNH BẰNG THỊ GIÁC: Phôi thẻ, Toàn bộ chỉ số, toàn bộ Khối Hitbox/Physics, Style Đỏ, Style Xanh.
        🔹 KIỂM TRA STYLE XANH: In đậm 🔵 **STYLE XANH** trên cùng 1 dòng và soi độ khớp với sơ đồ lùi khối.
        🔹 Dựa trên Chỉ số + Style + Hitbox (chỉ nêu hitbox nếu thật sự hợp/lệch), kết luận: Thẻ này PHÙ HỢP, LỆCH PHA hay CẦN BÙ ĐẮP.
        
        ===
        PHẦN 2: PHÂN BỔ PP & QUY HOẠCH (Giữa === 1 và 2)
        🔹 LUẬT TOÁN HỌC PP (CẤM TÍNH SAI): Bạn bắt buộc phải tra cứu Bảng Chi Phí sau để tính điểm: Cấp 4 tốn 4 PP | Cấp 5 tốn 6 PP | Cấp 6 tốn 8 PP | Cấp 7 tốn 10 PP | Cấp 8 tốn 12 PP | Cấp 9 tốn 15 PP | Cấp 10 tốn 18 PP | Cấp 11 tốn 21 PP | Cấp 12 tốn 24 PP.
        🔹 Yêu cầu: Nêu rõ từng mục nâng bao nhiêu điểm và tốn bao nhiêu PP. Tổng số PP sử dụng phải bằng đúng dung lượng PP của thẻ.
        🔹 Đề xuất 1 Booster Slot 2 phù hợp.
        
        ===
        PHẦN 3: SO SÁNH AUTO & THỦ CÔNG (Giữa === 2 và 3)
        🔹 Bảng đối đầu (Auto vs Thủ công DNS).
        🔹 Manager Boosts (Đọc chữ Vàng/Cam dưới tên HLV).
        
        ===
        PHẦN 4: CÀI ĐẶT & KỸ NĂNG SA BÀN (Sau === thứ 3)
        🎯 Individual Instructions.
        🧩 Top 5 Skill bổ sung ưu tiên.
        🎙️ Insight Chốt Hạ.
        """
        config = types.GenerateContentConfig(system_instruction=system_instruction, temperature=0.1)
        
        comp_text = "ĐÂY LÀ ẢNH SO SÁNH (TRÁI: AUTO, PHẢI: THỦ CÔNG DNS)." if is_comp else ""
        context_prompt = f"Thông tin: {p_info} | Hệ: {eco}. {comp_text}"
        
        contents = [context_prompt] + img_list
        response = client.models.generate_content(model='gemini-1.5-flash', contents=contents, config=config)
        return clean_text_and_build_ui(response.text)
    except Exception as e:
        return f"[LỖI HỆ THỐNG]: {str(e)}"

# ---------------------------------------------------------
# 5. XỬ LÝ SỰ KIỆN & HIỂN THỊ KẾT QUẢ (GIỮ NGUYÊN 4 TAB)
# ---------------------------------------------------------
if st.button("🚀 BẮT ĐẦU PHÂN TÍCH VIP"):
    if not uploaded_players and not uploaded_managers: 
        st.error("Vui lòng tải ít nhất 1 ảnh Cầu thủ hoặc HLV!")
    else:
        with st.spinner("Đang trích xuất Báo cáo Sa bàn..."):
            images_to_send = []
            is_only_manager = (len(uploaded_managers) > 0 and len(uploaded_players) == 0)
            
            if uploaded_players:
                for f in uploaded_players:
                    img = Image.open(f); img.thumbnail((1000, 1000))
                    images_to_send.append(img)
            if uploaded_managers:
                for f in uploaded_managers:
                    img = Image.open(f); img.thumbnail((1000, 1000))
                    images_to_send.append(img)
                
            st.session_state['analysis_report'] = execute_tactical_analysis(images_to_send, player_info, ecosystem, is_comparison, is_only_manager)
            st.session_state['report_time'] = vn_time_now.strftime("%d/%m/%Y | %H:%M:%S")
            images_to_send.clear()
            gc.collect()

if 'analysis_report' in st.session_state:
    parts = st.session_state['analysis_report'].split("===")
    
    tab1_c = parts[0] if len(parts) > 0 else "Đang xử lý..."
    tab2_c = parts[1] if len(parts) > 1 else "Không có dữ liệu Quy hoạch."
    tab3_c = parts[2] if len(parts) > 2 else "Không có dữ liệu Vận hành / So sánh."
    tab4_c = parts[3] if len(parts) > 3 else "Không có dữ liệu Cài đặt."
    
    report_time = st.session_state.get('report_time', vn_time_now.strftime("%d/%m/%Y | %H:%M:%S"))
    
    t1, t2, t3, t4 = st.tabs([
        "🪪 THẨM ĐỊNH & TRIẾT LÝ", 
        "🛠️ PHÂN BỔ PP & QUY HOẠCH", 
        "⚖️ SO SÁNH AUTO & THỦ CÔNG", 
        "🎯 CÀI ĐẶT & KỸ NĂNG SA BÀN"
    ])
    
    footer_text_color = "#64748B" if is_daytime else "#94A3B8"
    
    def format_tab(content):
        return f"""<div class="vip-card">
            <div style="text-align:center; margin-bottom: 18px;">
                <img src="{logo_url}" class="vip-logo-3d">
            </div>
            <div class="vip-text">{content.strip()}</div>
            <div class="vip-footer">
                <span style="color: {footer_text_color}; font-style: italic; font-weight: 600;">Đồng bộ lúc: {report_time}</span>
                <span style="color: {label_color}; font-weight: 900; text-shadow: 0px 1px 2px rgba(184, 134, 11, 0.4);">DNS TACTICAL ARCHITECT <br> © 2026 DN SIM MY LEAGUE. All rights reserved.</span>
            </div>
        </div>"""

    with t1: st.markdown(format_tab(tab1_c), unsafe_allow_html=True)
    with t2: st.markdown(format_tab(tab2_c), unsafe_allow_html=True)
    with t3: st.markdown(format_tab(tab3_c), unsafe_allow_html=True)
    with t4: st.markdown(format_tab(tab4_c), unsafe_allow_html=True)
    
    with st.expander("Bấm vào đây để Copy văn bản thô (Dành cho Team Content)"):
        raw_text_clean = st.session_state['analysis_report'].replace("<b>", "").replace("</b>", "").replace("<div class='warning-box'>", "").replace("</div>", "").replace("===", "\n\n")
        # Xóa các tag BOX khi copy thô
        raw_text_clean = re.sub(r'<details.*?>', '', raw_text_clean)
        raw_text_clean = re.sub(r'</details>', '', raw_text_clean)
        raw_text_clean = re.sub(r'<summary.*?>', '[', raw_text_clean)
        raw_text_clean = re.sub(r'</summary>', ']\n', raw_text_clean)
        raw_text_clean = re.sub(r'<div class="expander-content">', '', raw_text_clean)
        raw_text_clean = raw_text_clean.replace('<br>', '\n')
        st.text_area("Văn bản gốc:", value=raw_text_clean, height=200)
