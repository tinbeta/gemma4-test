<p align="center">
  <img src="public/banner.png" alt="Gemma 4 Playground" width="100%">
</p>

<p align="center">
  <strong>Giao diện chatbot chuyên nghiệp để khám phá sức mạnh của Gemma 4 — mô hình AI mã nguồn mở từ Google.</strong>
</p>

<p align="center">
  <a href="https://ai.google.dev/gemma"><img src="https://img.shields.io/badge/Model-Gemma_4-8957e5?style=for-the-badge&logo=google&logoColor=white" alt="Gemma 4"></a>
  <a href="https://aistudio.google.com/apikey"><img src="https://img.shields.io/badge/API-Gemini_API-4285F4?style=for-the-badge&logo=google&logoColor=white" alt="Gemini API"></a>
  <a href="#"><img src="https://img.shields.io/badge/Deploy-Vercel-000000?style=for-the-badge&logo=vercel&logoColor=white" alt="Vercel"></a>
  <a href="https://www.apache.org/licenses/LICENSE-2.0"><img src="https://img.shields.io/badge/License-Apache_2.0-green?style=for-the-badge" alt="License"></a>
</p>

---

## ✨ Tính năng

| Tính năng | Mô tả |
|---|---|
| 💬 **Chat thông minh** | Hội thoại nhiều lượt với bộ nhớ ngữ cảnh đầy đủ |
| 🖼️ **Hiểu hình ảnh** | Upload ảnh và hỏi AI phân tích (multimodal) |
| 🔍 **Google Search** | Tra cứu thông tin real-time từ web |
| ⚡ **Function Calling** | Gọi hàm tự động (thời tiết, tìm địa điểm, tính toán) |
| 🧠 **Thinking Mode** | Chế độ suy luận từng bước (Chain of Thought) |
| ✍️ **Markdown & Code** | Hiển thị code với syntax highlighting (Tokyo Night theme) |
| 🔑 **Bring Your Own Key** | Nhập API Key riêng để test, không cần cấu hình server |
| 🌙 **Dark Mode** | Giao diện tối chuyên nghiệp, tối ưu cho mắt |

## 🏗️ Kiến trúc

```
gemma4/
├── 🌐 public/              # Frontend tĩnh (Vercel)
│   └── index.html           # Giao diện chatbot
├── ⚡ api/                  # Serverless functions (Vercel)
│   ├── send.py              # API endpoint chính
│   └── requirements.txt     # Dependencies cho serverless
├── 🐍 app.py                # Flask server (chạy local)
├── 📁 templates/
│   └── index.html           # Template cho Flask
├── 🧪 test/                 # Bộ test các tính năng
│   ├── 01_text_gen.py
│   ├── 02_system_instruction.py
│   ├── 03_chat_history.py
│   ├── 04_image_understanding.py
│   ├── 05_function_calling.py
│   ├── 06_google_search.py
│   └── run_all_tests.sh
├── vercel.json              # Cấu hình Vercel
├── requirements.txt         # Dependencies
└── .env                     # API Key (local only)
```

## 🚀 Bắt đầu nhanh

### Cách 1: Chạy trên Local

```bash
# 1. Clone repo
git clone https://github.com/your-username/gemma4-playground.git
cd gemma4-playground

# 2. Tạo môi trường ảo
python3 -m venv venv
source venv/bin/activate

# 3. Cài dependencies
pip install flask flask-cors google-genai python-dotenv

# 4. Cấu hình API Key
echo "GEMINI_API_KEY=your_key_here" > .env

# 5. Chạy server
./run_web_ui.sh
```

Truy cập 👉 **http://127.0.0.1:5001**

### Cách 2: Deploy lên Vercel

```bash
# 1. Cài Vercel CLI
npm i -g vercel

# 2. Deploy
vercel --prod
```

> **Lưu ý:** Phiên bản Vercel không cần `.env` — người dùng tự nhập API Key trên giao diện.

## 🔑 Lấy API Key

1. Truy cập **[Google AI Studio](https://aistudio.google.com/apikey)**
2. Đăng nhập bằng tài khoản Google
3. Nhấn **"Create API Key"**
4. Copy key và dán vào ô API Key trên giao diện

> ⚠️ **Bảo mật:** API Key là thông tin nhạy cảm. Test xong nên xóa key và tạo key mới khi cần.

## 🤖 Mô hình hỗ trợ

| Mô hình | Loại | Context | Điểm mạnh |
|---|---|---|---|
| `gemma-4-31b-it` | Dense | 256K | Suy luận mạnh, #3 Open Model trên Arena AI |
| `gemma-4-26b-a4b-it` | MoE (4B active) | 256K | Nhanh hơn, hiệu quả năng lượng, #6 Arena AI |

## ⚡ Function Calling

Khi bật Function Calling, AI có thể tự động gọi 3 hàm mẫu:

```python
get_weather(location)        # Lấy thời tiết → "Thời tiết Hà Nội?"
search_places(city, category) # Tìm địa điểm  → "Nhà hàng ngon ở Đà Nẵng?"
calculate(expression)         # Tính toán      → "Tính 15% của 2.500.000"
```

**Luồng hoạt động:**
```
User → Gemma 4 → Quyết định gọi hàm → Thực thi → Trả kết quả → Gemma 4 tổng hợp → User
```

## 🧪 Bộ Test Scripts

Chạy toàn bộ 6 test để kiểm tra các tính năng của Gemma 4:

```bash
cd test/
chmod +x run_all_tests.sh
./run_all_tests.sh
```

| Script | Tính năng |
|---|---|
| `01_text_gen.py` | Sinh văn bản cơ bản |
| `02_system_instruction.py` | System Prompt tùy chỉnh |
| `03_chat_history.py` | Hội thoại nhiều lượt |
| `04_image_understanding.py` | Phân tích hình ảnh |
| `05_function_calling.py` | Gọi hàm tự động |
| `06_google_search.py` | Tìm kiếm Google |

## 🛠️ Tech Stack

- **Frontend:** Vanilla HTML/CSS/JS, Marked.js, Highlight.js
- **Backend (Local):** Flask + Flask-CORS
- **Backend (Vercel):** Python Serverless Functions
- **AI:** Google Gemini API (`google-genai` SDK)
- **Design:** GitHub Dark Theme, Glassmorphism

## 📄 License

Dự án này được phân phối dưới giấy phép [Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0) — giống với mô hình Gemma 4.

---

<p align="center">
  <sub>Built with ❤️ for the Gemma 4 community</sub>
</p>
