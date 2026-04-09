import os
from google import genai
from google.genai import types
from _key_helper import get_api_key

api_key = get_api_key()

client = genai.Client(api_key=api_key)

image_path = "japan_temple.png"

if not os.path.exists(image_path):
    print(f"Error: {image_path} not found.")
    exit(1)

with open(image_path, "rb") as f:
    image_bytes = f.read()

print("--- Đang test Gemma 4 Hiểu Hình ảnh ---")
response = client.models.generate_content(
    model="gemma-4-26b-a4b-it",
    contents=[
        types.Part.from_bytes(data=image_bytes, mime_type="image/png"),
        "Mô tả hình ảnh này trong 2-3 câu giống như đang viết chú thích cho một tạp chí du lịch Nhật Bản."
    ]
)
print(response.text)
