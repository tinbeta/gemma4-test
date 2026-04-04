import os
from google import genai
from dotenv import load_dotenv

# Load API key from .env
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("Error: GEMINI_API_KEY not found in .env file.")
    exit(1)

client = genai.Client(api_key=api_key)

print("--- Đang test Gemma 4 Tạo văn bản (26B MoE) ---")
response = client.models.generate_content(
    model="gemma-4-26b-a4b-it",
    contents="So sánh ramen và udon qua 3 tiêu chí: nước dùng, kết cấu sợi mì và mùa ăn ngon nhất."
)
print(response.text)

print("\n--- Đang test Gemma 4 Tạo văn bản (31B Dense) ---")
response = client.models.generate_content(
    model="gemma-4-31b-it",
    contents="Ưu điểm chính của mô hình Dense so với Mixture of Experts (MoE) là gì?"
)
print(response.text)
