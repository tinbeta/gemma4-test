import os
from google import genai
from dotenv import load_dotenv

# Load API key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)
chat = client.chats.create(model="gemma-4-26b-a4b-it")

print("--- Đang test Gemma 4 Trò chuyện (Lượt 1) ---")
response = chat.send_message("Ba tòa lâu đài nổi tiếng nhất Nhật Bản là gì?")
print(f"Người dùng: Ba tòa lâu đài nổi tiếng nhất Nhật Bản là gì?\nGemma: {response.text}\n")

print("--- Đang test Gemma 4 Trò chuyện (Lượt 2) ---")
response = chat.send_message("Tòa nào nên ghé thăm vào mùa xuân để ngắm hoa anh đào?")
print(f"Người dùng: Tòa nào nên ghé thăm vào mùa xuân để ngắm hoa anh đào?\nGemma: {response.text}\n")
