#!/bin/bash

# Activate virtual environment
source venv/bin/activate

echo "========================================"
echo "   Hệ thống Chạy Test Gemma 4 API"
echo "========================================"

echo ""
echo "1. Tạo văn bản cơ bản..."
python3 01_text_gen.py

echo ""
echo "2. Chỉ dẫn hệ thống (System Instructions)..."
python3 02_system_instruction.py

echo ""
echo "3. Trò chuyện nhiều lượt (Chat)..."
python3 03_chat_history.py

echo ""
echo "4. Hiểu hình ảnh (Multimodal)..."
python3 04_image_understanding.py

echo ""
echo "5. Gọi hàm (Function Calling)..."
python3 05_function_calling.py

echo ""
echo "6. Tra cứu Google Search..."
python3 06_google_search.py

echo ""
echo "========================================"
echo "          Hoàn tất kiểm tra"
echo "========================================"
