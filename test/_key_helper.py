import os
import sys
from getpass import getpass


def get_api_key():
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if api_key:
        return api_key

    try:
        api_key = getpass("Nhập GEMINI_API_KEY để chạy test: ").strip()
    except EOFError:
        api_key = ""

    if not api_key:
        print("Error: Chưa có GEMINI_API_KEY. Hãy nhập key khi được hỏi hoặc export biến môi trường tạm thời cho phiên shell hiện tại.")
        sys.exit(1)

    return api_key
