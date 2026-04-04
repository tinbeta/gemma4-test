import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load API key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)

print("--- Đang test Gemma 4 Tra cứu Google Search ---")
response = client.models.generate_content(
    model="gemma-4-26b-a4b-it",
    contents="Lịch mùa hoa anh đào ở Tokyo năm nay là khi nào?",
    config=types.GenerateContentConfig(
        tools=[{"google_search":{}}]
    ),
)

print(f"Phản hồi từ mô hình: {response.text}")

# Truy cập metadata tra cứu để lấy nguồn trích dẫn
if response.candidates and response.candidates[0].grounding_metadata:
    print("\n--- Nguồn Trích dẫn (Citations) ---")
    for chunk in response.candidates[0].grounding_metadata.grounding_chunks:
        if chunk.web:
            print(f"Nguồn: {chunk.web.title} — {chunk.web.uri}")
else:
    print("\nKhông tìm thấy dữ liệu trích dẫn.")
