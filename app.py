import streamlit as st
import requests
from PIL import Image
import io
import base64
import os
from dotenv import load_dotenv

# Tải biến môi trường từ file .env (chỉ dùng khi chạy cục bộ)
load_dotenv()

# --- Cấu hình mô hình Roboflow ---
# API Key được lấy từ biến môi trường hoặc Streamlit Secrets
KHOA_API = os.getenv("ROBOFLOW_API_KEY")
TEN_MO_HINH = "tomato-leaf-diseases-2-7rwwa"
PHIEN_BAN = "1"
DIA_CHI_API = f"https://serverless.roboflow.com/{TEN_MO_HINH}/{PHIEN_BAN}?api_key={KHOA_API}"

# --- Cơ sở dữ liệu kiến thức về bệnh cà chua (KEY khớp với tên lớp từ Roboflow) ---
disease_database_content = {
    'Bacterial_spot': {
        'display_name': 'Đốm vi khuẩn (Bacterial Spot)',
        'description': """
        **Tác nhân:** Do vi khuẩn *Xanthomonas* gây ra.
        **Điều kiện phát triển:** Bệnh phát triển mạnh trong điều kiện thời tiết ấm, ẩm và mưa nhiều. Vi khuẩn lây lan qua nước mưa, nước tưới bắn lên lá và qua các vết thương cơ giới.
        **Triệu chứng:** Vết bệnh là những đốm nhỏ, sũng nước, màu nâu đến đen, thường có hình dạng góc cạnh. Các đốm có thể có quầng vàng bao quanh và phần trung tâm sau đó khô lại, rách ra tạo thành hiệu ứng "lủng lỗ". Bệnh có thể tấn công cả lá, thân và quả.
        """,
        'solution': """
        #### 🌿 Hành động ngay lập tức
        * **Cắt tỉa:** Loại bỏ và tiêu hủy ngay các lá, cành bị bệnh để giảm nguồn lây nhiễm.
        * **Không làm việc khi cây ướt:** Tránh tỉa cành, thu hái hoặc đi lại trong vườn khi lá cây còn ướt vì sẽ làm lây lan vi khuẩn.

        #### 💧 Cải thiện phương pháp canh tác
        * **Tưới gốc:** Luôn tưới nước vào gốc cây, tránh làm ướt lá.
        * **Luân canh:** Không trồng cà chua hoặc các cây cùng họ (ớt, khoai tây) trên đất đã nhiễm bệnh trong ít nhất 1-2 năm.

        #### 💊 Sử dụng thuốc bảo vệ thực vật
        * **Thuốc gốc Đồng (Copper):** Phun các loại thuốc gốc đồng có tác dụng kìm hãm sự phát triển của vi khuẩn. Có thể kết hợp với Mancozeb để tăng hiệu quả.
        * Phun phòng định kỳ, đặc biệt là trước và sau các trận mưa khi thời tiết ấm.
        """,
        'prevention': """
        * **Sử dụng hạt giống sạch bệnh:** Chọn mua hạt giống từ các nguồn uy tín.
        * **Vệ sinh đồng ruộng:** Dọn sạch tàn dư cây trồng từ vụ trước.
        * **Phủ gốc:** Sử dụng màng phủ hoặc rơm rạ để hạn chế đất chứa mầm bệnh bắn lên cây.
        """
    },
    'Late_blight': {
        'display_name': 'Bệnh Mốc sương / Sương mai (Late Blight)',
        'description': """
        **Tác nhân:** Do nấm *Phytophthora infestans* gây ra. Đây là một trong những bệnh nguy hiểm và có sức tàn phá lớn nhất trên cà chua, còn được gọi là **bệnh sương mai** hay **cháy muộn**.
        **Điều kiện phát triển:** Bệnh bùng phát mạnh mẽ trong điều kiện thời tiết **mát mẻ (18-22°C) và độ ẩm rất cao (>90%)**, đặc biệt là khi có mưa phùn kéo dài.
        **Triệu chứng:** Vết bệnh lớn, không có hình dạng nhất định, màu xanh xám như úng nước, sau đó nhanh chóng chuyển sang nâu đen. Dưới mặt lá ở rìa vết bệnh thường có lớp mốc trắng như sương. Bệnh có thể làm toàn bộ cây chết rũ trong vài ngày.
        """,
        'solution': """
        #### 🌿 Hành động ngay lập tức (Rất khẩn cấp!)
        * **Tiêu hủy ngay:** Cắt bỏ và cho ngay vào túi nilon kín để tiêu hủy bất kỳ bộ phận nào có dấu hiệu bệnh. Tốc độ lây lan của bệnh này cực nhanh.
        * Nếu cây bị nặng, phải nhổ bỏ và tiêu hủy cả cây, rắc vôi bột vào vị trí vừa nhổ.

        #### 💧 Cải thiện phương pháp canh tác
        * **Giữ lá khô ráo:** Đây là yếu tố quan trọng nhất. Chỉ tưới gốc, không tưới lên lá.
        * **Tăng tối đa sự thông thoáng:** Trồng thưa, tỉa cành, làm giàn để không khí lưu thông tốt.

        #### 💊 Sử dụng thuốc bảo vệ thực vật
        * **Phòng bệnh là chính:** Khi thời tiết thuận lợi cho bệnh, phải phun phòng định kỳ 7-10 ngày/lần.
        * **Thuốc hóa học:** Sử dụng các loại thuốc có hoạt chất **Mancozeb, Chlorothalonil** (phun phòng), hoặc các thuốc đặc trị như **Metalaxyl, Cymoxanil, Azoxystrobin** (phun khi bệnh chớm xuất hiện).
        """,
        'prevention': """
        * **Chọn giống kháng bệnh:** Đây là biện pháp phòng trừ hiệu quả và bền vững nhất.
        * **Luân canh:** Không trồng cà chua, khoai tây ở cùng vị trí trong ít nhất 3-4 năm.
        * **Theo dõi thời tiết:** Chú ý dự báo thời tiết, nếu có mưa nhiều và trời mát, cần phun phòng ngay.
        """
    },
    'Leaf_Mold': {
        'display_name': 'Bệnh Mốc lá (Leaf Mold)',
        'description': """
        **Tác nhân:** Do nấm *Passalora fulva* (tên cũ *Fulvia fulva*) gây ra.
        **Điều kiện phát triển:** Bệnh phát triển mạnh trong điều kiện **độ ẩm rất cao (trên 85%)** và nhiệt độ ấm, đặc biệt phổ biến trong nhà kính hoặc các khu vực kém thông thoáng.
        **Triệu chứng:** Mặt trên lá xuất hiện các đốm màu xanh nhạt hoặc vàng, không có đường viền rõ rệt. Đặc điểm nhận dạng quan trọng nhất là ở **mặt dưới lá**, tương ứng với các đốm vàng ở mặt trên, sẽ có một lớp nấm mốc mịn như nhung màu xanh ô liu, sau đó chuyển dần sang màu nâu.
        """,
        'solution': """
        #### 🌿 Hành động ngay lập tức
        * **Cắt tỉa:** Loại bỏ sớm các lá bị nhiễm bệnh ở tầng dưới để giảm áp lực mầm bệnh.

        #### 💧 Cải thiện phương pháp canh tác (Quan trọng nhất)
        * **Giảm độ ẩm:** Tăng cường thông gió tối đa (mở cửa nhà kính, sử dụng quạt).
        * **Tỉa lá:** Tỉa bớt các lá già, lá gốc để tạo sự thông thoáng cho tán cây.
        * **Tưới nước buổi sáng:** Tưới vào gốc cây vào buổi sáng để bề mặt lá nhanh khô. Tránh tưới vào buổi chiều tối.

        #### 💊 Sử dụng thuốc bảo vệ thực vật
        * Có thể sử dụng các loại thuốc trừ nấm có hoạt chất như **Mancozeb, Chlorothalonil, hoặc các thuốc gốc Đồng**.
        * Phun kỹ vào mặt dưới của lá.
        """,
        'prevention': """
        * **Giống kháng bệnh:** Nhiều giống cà chua hiện đại có khả năng kháng bệnh mốc lá.
        * **Vệ sinh nhà kính/vườn:** Dọn dẹp sạch tàn dư thực vật sau vụ thu hoạch.
        * **Mật độ trồng hợp lý:** Không trồng cây quá dày.
        """
    },
    'Septoria_leaf_spot': {
        'display_name': 'Đốm lá Septoria (Septoria Leaf Spot)',
        'description': """
        **Tác nhân:** Do nấm *Septoria lycopersici* gây ra.
        **Điều kiện phát triển:** Bệnh phát triển mạnh trong điều kiện thời tiết ấm và ẩm ướt, lây lan chủ yếu qua nước bắn (mưa, tưới tiêu) từ đất lên lá.
        **Triệu chứng:** Rất nhiều đốm nhỏ (2-5mm) hình tròn, có **tâm màu xám trắng hoặc nâu nhạt và viền màu nâu sẫm/đen** rất đặc trưng. Bệnh thường bắt đầu từ các lá già phía dưới rồi lan dần lên trên, làm lá vàng, khô và rụng sớm.
        """,
        'solution': """
        #### 🌿 Hành động ngay lập tức
        * **Cắt tỉa:** Cắt bỏ và tiêu hủy ngay lập tức tất cả các lá bị nhiễm bệnh. **Không được vứt lá bệnh ra vườn hoặc ủ làm phân compost.**

        #### 💧 Cải thiện phương pháp canh tác
        * **Tưới nước đúng cách:** Chỉ tưới vào gốc cây, không tưới lên lá.
        * **Tăng độ thông thoáng:** Tỉa bớt các cành lá ở dưới gốc để không khí lưu thông.
        * **Phủ gốc:** Dùng rơm rạ hoặc màng phủ nông nghiệp để ngăn nấm bệnh từ đất bắn lên lá.

        #### 💊 Sử dụng thuốc bảo vệ thực vật
        * **Thuốc sinh học/hữu cơ:** Sử dụng các loại thuốc gốc Đồng (Copper), *Bacillus subtilis*.
        * **Thuốc hóa học:** Sử dụng thuốc có hoạt chất **Chlorothalonil** hoặc **Mancozeb**.
        """,
        'prevention': """
        * **Luân canh:** Không trồng cà chua, ớt, khoai tây ở cùng một vị trí trong 2-3 năm.
        * **Vệ sinh đồng ruộng:** Dọn dẹp sạch sẽ tàn dư cây trồng sau mỗi vụ.
        * **Chọn giống kháng bệnh:** Ưu tiên sử dụng các giống có khả năng kháng bệnh Septoria.
        """
    },
    'Yellow_Leaf_Curl_Virus': {
        'display_name': 'Bệnh Xoăn vàng lá do Virus (Yellow Leaf Curl Virus)',
        'description': """
        **Tác nhân:** Do một nhóm virus phức tạp (TYLCV) gây ra.
        **Phương thức lây truyền:** Virus **không tự lây lan** mà được truyền từ cây bệnh sang cây khỏe chủ yếu thông qua côn trùng chích hút là **bọ phấn trắng (whitefly)**.
        **Triệu chứng:** Cây bị nhiễm bệnh sẽ còi cọc, chậm phát triển nghiêm trọng. Lá non bị xoăn lại, cong lên trên, mép lá vàng. Kích thước lá nhỏ hơn bình thường, lá dày và giòn. Cây rất ít ra hoa hoặc không đậu quả, gây thất thu năng suất gần như hoàn toàn.
        """,
        'solution': """
        ### **LƯU Ý QUAN TRỌNG: KHÔNG CÓ THUỐC CHỮA BỆNH DO VIRUS!**
        Mọi biện pháp đều tập trung vào việc **xử lý cây bệnh** và **kiểm soát côn trùng truyền bệnh**.

        #### 🌿 Hành động ngay lập tức
        * **Nhổ bỏ và tiêu hủy:** Ngay khi phát hiện cây có triệu chứng, cần nhổ bỏ toàn bộ cây (bao gồm cả rễ), cho vào túi nilon đen và mang đi tiêu hủy xa khu vực trồng. Đây là hành động quan trọng nhất để loại bỏ nguồn lây.

        #### 🦟 Kiểm soát bọ phấn trắng (Vector truyền bệnh)
        * **Bẫy dính màu vàng:** Treo các tấm bẫy dính màu vàng xung quanh vườn để thu hút và tiêu diệt bọ phấn trưởng thành.
        * **Phun thuốc trừ sâu:** Sử dụng các loại thuốc có hoạt chất như **Dinotefuran, Acetamiprid, Imidacloprid** để kiểm soát bọ phấn. Có thể dùng các loại thuốc sinh học như dầu Neem, nấm ký sinh (Beauveria bassiana) khi mật độ thấp.
        """,
        'prevention': """
        * **Sử dụng cây giống khỏe, sạch bệnh:** Mua cây giống từ các vườn ươm uy tín.
        * **Nhà lưới/nhà kính:** Sử dụng nhà lưới có mắt lưới đủ nhỏ để ngăn bọ phấn xâm nhập là biện pháp hiệu quả nhất.
        * **Vệ sinh vườn tược:** Dọn dẹp cỏ dại xung quanh vườn vì đây là nơi trú ngụ của bọ phấn.
        * **Chọn giống kháng Virus:** Đây là giải pháp bền vững và hiệu quả hàng đầu.
        """
    },
    'healthy': {
        'display_name': 'Lá Khỏe mạnh (Healthy)',
        'description': """
        ### **🎉 Chúc mừng, cây cà chua của bạn đang khỏe mạnh!**
        Lá cây xanh tốt, không có dấu hiệu của đốm bệnh, nấm mốc hay biến dạng. Đây là một tín hiệu tuyệt vời cho thấy bạn đang chăm sóc cây rất tốt.
        """,
        'solution': """
        ### ✅ Làm thế nào để giữ cây luôn khỏe mạnh?
        * **Duy trì tưới nước đều đặn:** Tiếp tục tưới nước vào gốc, giữ độ ẩm cho đất ổn định nhưng không bị úng nước.
        * **Bón phân cân đối:** Cung cấp dinh dưỡng đầy đủ và cân đối (Đạm, Lân, Kali và các vi lượng) theo từng giai đoạn sinh trưởng của cây (cây con, ra hoa, nuôi quả).
        * **Tỉa lá định kỳ:** Tỉa bỏ các lá già ở gốc để cây luôn thông thoáng, tập trung dinh dưỡng nuôi quả và phòng ngừa sâu bệnh.
        * **Thăm vườn thường xuyên:** Dành thời gian kiểm tra cây mỗi ngày để phát hiện sớm nhất bất kỳ dấu hiệu bất thường nào.
        """,
        'prevention': """
        Phòng bệnh hơn chữa bệnh. Hãy tiếp tục duy trì các biện pháp phòng ngừa tốt nhất:
        * **Giữ vườn sạch sẽ, thông thoáng.**
        * **Luôn tưới nước vào gốc.**
        * **Theo dõi sự xuất hiện của sâu bệnh hại để hành động sớm.**
        * **Luân canh cây trồng sau mỗi vụ thu hoạch.**
        """
    }
}

def du_doan_benh(anh):
    """Gửi ảnh đến API Roboflow để nhận dạng."""
    bo_dem = io.BytesIO()
    anh.save(bo_dem, quality=90, format="JPEG")
    anh_mahoa = base64.b64encode(bo_dem.getvalue()).decode("utf-8")
    phan_hoi = requests.post(DIA_CHI_API, data=anh_mahoa, headers={"Content-Type": "application/x-www-form-urlencoded"})
    return phan_hoi.json()

# --- Giao diện người dùng (UI) ---
st.set_page_config(page_title="Ứng dụng Nhận diện Bệnh Lá Cà Chua", page_icon="🍅", layout="centered")

# Áp dụng CSS tùy chỉnh để làm đẹp giao diện (Giữ nguyên để không thay đổi giao diện)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700;900&display=swap');

    html, body, [class*="css"] {
        font-family: 'Roboto', sans-serif;
        color: #333;
        font-size: 1.1em;
    }
    .stApp {
        background-color: #f0f2f6;
    }
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 1rem;
        padding-right: 1rem;
        max-width: 700px;
        margin: auto;
    }
    h1 {
        color: #B22222; /* Màu đỏ nổi bật hơn (FireBrick) */
        margin-bottom: 2rem; /* Tăng khoảng cách dưới tiêu đề */
        font-size: 3em;
        font-weight: 700;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    
    h1 a {
        display: none !important;
    }
    
    .stFileUploader {
        border: 2px dashed #a7d9b5;
        border-radius: 10px;
        background-color: #e6ffe6;
        min-height: 150px;
        position: relative;
        padding: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.3s ease-in-out;
        overflow: hidden;
    }
    .stFileUploader:hover {
        border-color: #28a745;
        background-color: #d4ffd4;
    }
    .stFileUploader::before {
        content: 'Bấm vào đây để chụp hoặc tải ảnh lên';
        display: block;
        position: absolute;
        top: 35%;
        left: 50%;
        transform: translate(-50%, -50%);
        color: #c62828;
        font-weight: 900;
        font-size: 1.2rem;
        pointer-events: none;
        text-align: center;
        width: 90%;
        z-index: 2;
    }
    .stFileUploader:has([data-testid="stFileUploaderFile"])::before {
        content: 'Bấm vào đây để chụp hoặc tải ảnh khác';
    }
    .stFileUploader [data-testid="stFileUploaderDropzoneInstructions"] {
        display: none !important;
    }
    .stFileUploader [data-testid="stFileUploaderDropzone"],
    .stFileUploader [data-testid="stFileUploaderDropzone"] * {
        background: transparent !important;
        border: none !important;
    }
    .stFileUploader [data-testid="stFileUploaderDropzone"] button {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        opacity: 0;
        cursor: pointer;
        z-index: 1;
    }
    .stFileUploader [data-testid="stFileUploaderFile"] {
        position: absolute;
        bottom: 15%;
        left: 50%;
        transform: translateX(-50%);
        display: flex;
        align-items: center;
        justify-content: center;
        width: 100%;
        padding: 0 1rem;
        font-size: 0.9em;
        color: #333;
        z-index: 0;
    }
    .stImage {
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .stSpinner > div > div {
        color: #28a745 !important;
    }
    .stSuccess, .stInfo, .stWarning, .stError {
        border-radius: 8px;
        padding: 18px;
        margin-top: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.08);
        font-size: 1.4em !important;
        line-height: 1.6;
    }
    .stSuccess {
        background-color: #d4edda;
        color: #155724;
        border-left: 6px solid #28a745;
        font-weight: 700 !important;
    }
    .stWarning {
        background-color: #fff3cd;
        color: #856404;
        border-left: 5px solid #ffc107;
    }
    .stError {
        background-color: #f8d7da;
        color: #721c24;
        border-left: 5px solid #dc3545;
    }
    .footer {
        text-align: center;
        margin-top: 30px;
        padding-top: 15px;
        border-top: 1px solid #eee;
        color: #777;
        font-size: 0.9em;
    }
    /* CSS cho expander */
    .stExpander {
        border: 1px solid #ddd;
        border-radius: 10px;
        background-color: #ffffff;
    }
    .stExpander header {
        font-size: 1.2em !important;
        font-weight: 700 !important;
        color: #B22222 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- Luồng chính của ứng dụng ---
st.markdown("<h1 style='text-align: center;'>🍅 ỨNG DỤNG AI NHẬN DIỆN BỆNH QUA LÁ CÀ CHUA 🍃</h1>", unsafe_allow_html=True)

tep_anh = st.file_uploader(
    label="Tải ảnh lên",
    type=["jpg", "jpeg", "png"],
    help="Hỗ trợ các định dạng: JPG, JPEG, PNG.",
    label_visibility="collapsed"
)

if tep_anh is not None:
    anh = Image.open(tep_anh).convert("RGB")
    st.image(anh, caption="📷 Ảnh đã tải lên", use_container_width=True)

    with st.spinner("🔍 Đang phân tích... Vui lòng chờ ⏳"):
        ket_qua = du_doan_benh(anh)

    # Xử lý kết quả trả về từ API
    du_doan = ket_qua.get("predictions", [])
    if du_doan:
        benh = du_doan[0]
        ten_benh_goc = benh["class"]
        do_tin_cay = benh["confidence"] * 100

        # Lấy thông tin chi tiết từ cơ sở dữ liệu nội bộ
        info = disease_database_content.get(ten_benh_goc)

        if info:
            st.success(f"**Phát hiện:** {info['display_name']} (Độ tin cậy: {do_tin_cay:.1f}%)")

            # Sử dụng expander để hiển thị thông tin chi tiết một cách gọn gàng
            with st.expander("📝 Xem chi tiết và hướng dẫn xử lý"):
                st.markdown("### Mô tả")
                st.markdown(info['description'])
                
                st.markdown("### ✅ Hướng dẫn xử lý")
                st.markdown(info['solution'])
                
                st.markdown("### 🌱 Hướng dẫn phòng trừ cho vụ sau")
                st.markdown(info['prevention'])
        else:
            # Xử lý trường hợp tên bệnh từ Roboflow không có trong database
            formatted_ten_benh = ten_benh_goc.replace('_', ' ').title()
            st.warning(f"**Phát hiện:** {formatted_ten_benh} (Độ tin cậy: {do_tin_cay:.1f}%)")
            st.error("Rất tiếc, chưa có thông tin chi tiết cho loại bệnh này trong cơ sở dữ liệu.")
    else:
        st.warning("🥺 Không phát hiện được bệnh nào. Vui lòng thử ảnh khác hoặc đảm bảo ảnh rõ ràng.")

# --- Footer ---
st.markdown("---")
st.markdown('<div class="footer">Dự án được thực hiện bởi nhóm nghiên cứu AI.</div>', unsafe_allow_html=True)
