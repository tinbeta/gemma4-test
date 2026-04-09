from google import genai
from _key_helper import get_api_key

api_key = get_api_key()

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
