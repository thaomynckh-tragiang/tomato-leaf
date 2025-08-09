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
        **Triệu chứng:** Rất nhiều đốm nhỏ (2-5mm) hình tròn, có **tâm màu xám trắng hoặc nâu nhạt và viền màu nâu sẫm/đen** rất đặc trưng
