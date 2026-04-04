import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load API key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)

print("--- Đang test Hệ thống Chỉ dẫn (System Instruction) ---")
response = client.models.generate_content(
    model="gemma-4-31b-it",
    config=types.GenerateContentConfig(
        system_instruction="Bạn là một trà sư người Việt am hiểu văn hóa Trà đạo. Hãy trả lời một cách điềm đạm, thi vị, sử dụng các ẩn dụ về thiên nhiên. Trả lời không quá 3 câu."
    ),
    contents="Mục đích của trà đạo là gì?"
)
print(response.text)
