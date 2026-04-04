#!/bin/bash

# Activate virtual environment
source venv/bin/activate

echo "========================================"
echo "   Khởi động Gemma 4 Web Interface"
echo "========================================"
echo "Đang mở server tại: http://127.0.0.1:5001"
echo "Nhấn Ctrl+C để dừng."
echo ""

# Run the app
python3 app.py
