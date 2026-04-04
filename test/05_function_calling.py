import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load API key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# Định nghĩa khai báo hàm
get_weather = {
    "name": "get_weather",
    "description": "Lấy thời tiết hiện tại cho một địa điểm cụ thể.",
    "parameters": {
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "Thành phố và Bang, ví dụ: 'Hà Nội, VN'",
            },
        },
        "required": ["location"],
    },
}

client = genai.Client(api_key=api_key)
tools = types.Tool(function_declarations=[get_weather])
config = types.GenerateContentConfig(tools=[tools])

print("--- Đang test Gemma 4 Gọi hàm (Function Calling) ---")
response = client.models.generate_content(
    model="gemma-4-26b-a4b-it",
    contents="Tôi có nên mang ô khi đi Kyoto hôm nay không?",
    config=config,
)

# Mô hình trả về một lệnh gọi hàm thay vì văn bản
if response.function_calls:
    for fc in response.function_calls:
        print(f"Hàm cần gọi: {fc.name}")
        print(f"ID: {fc.id}")
        print(f"Tham số: {fc.args}")
else:
    print("Không tìm thấy lệnh gọi hàm nào trong phản hồi.")
    print(response.text)
