import json
import math
import os
from http.server import BaseHTTPRequestHandler
from google import genai
from google.genai import types

SAMPLE_FUNCTIONS = [
    {
        "name": "get_weather",
        "description": "Lấy thông tin thời tiết hiện tại cho một địa điểm.",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "Tên thành phố"},
            },
            "required": ["location"],
        },
    },
    {
        "name": "search_places",
        "description": "Tìm kiếm các địa điểm du lịch, nhà hàng, khách sạn tại một thành phố.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "Tên thành phố"},
                "category": {"type": "string", "description": "Loại: 'restaurant', 'hotel', 'attraction', 'cafe'"},
            },
            "required": ["city", "category"],
        },
    },
    {
        "name": "calculate",
        "description": "Thực hiện phép tính toán học.",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {"type": "string", "description": "Biểu thức toán, ví dụ: '2 + 3 * 4'"},
            },
            "required": ["expression"],
        },
    },
]


def execute_function(name, args):
    if name == "get_weather":
        loc = args.get("location", "Unknown")
        return json.dumps({
            "location": loc, "temperature": "28°C",
            "condition": "Có mây, khả năng mưa rào buổi chiều",
            "humidity": "75%", "wind": "Gió nhẹ 12 km/h hướng Đông Nam",
            "forecast": "Ngày mai trời nắng, 32°C"
        }, ensure_ascii=False)
    elif name == "search_places":
        city = args.get("city", "")
        cat = args.get("category", "restaurant")
        places = {
            "restaurant": [
                {"name": f"Nhà hàng Phở Thìn - {city}", "rating": 4.5, "price": "$$"},
                {"name": f"Quán Bún Chả Hương Liên - {city}", "rating": 4.7, "price": "$$"},
                {"name": f"Nhà hàng Madame Hiền - {city}", "rating": 4.3, "price": "$$$"},
            ],
            "hotel": [
                {"name": f"Sofitel Legend - {city}", "rating": 4.8, "price": "$$$$"},
                {"name": f"JW Marriott - {city}", "rating": 4.6, "price": "$$$$"},
            ],
            "cafe": [
                {"name": f"Cộng Cà Phê - {city}", "rating": 4.4, "price": "$"},
                {"name": f"The Note Coffee - {city}", "rating": 4.2, "price": "$"},
            ],
            "attraction": [
                {"name": f"Hoàn Kiếm Lake - {city}", "rating": 4.7, "price": "Free"},
                {"name": f"Old Quarter - {city}", "rating": 4.6, "price": "Free"},
            ],
        }
        return json.dumps({"city": city, "category": cat, "results": places.get(cat, places["restaurant"])}, ensure_ascii=False)
    elif name == "calculate":
        expr = args.get("expression", "0")
        try:
            result = eval(expr, {"__builtins__": {}}, {"math": math, "abs": abs, "round": round, "pow": pow, "min": min, "max": max})
            return json.dumps({"expression": expr, "result": result}, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"expression": expr, "error": str(e)}, ensure_ascii=False)
    return json.dumps({"error": f"Unknown function: {name}"})


def build_contents(history):
    """Chuyển lịch sử chat từ JSON sang types.Content."""
    contents = []
    for msg in history:
        role = msg.get("role", "user")
        parts_raw = msg.get("parts", [])
        parts = []
        for p in parts_raw:
            if isinstance(p, str):
                parts.append(types.Part.from_text(text=p))
            elif isinstance(p, dict) and p.get("text"):
                parts.append(types.Part.from_text(text=p["text"]))
        if parts:
            contents.append(types.Content(role=role, parts=parts))
    return contents


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            self._respond(400, {"error": "Invalid JSON"})
            return

        api_key = data.get("api_key", "").strip() or os.getenv("GEMINI_API_KEY", "")
        if not api_key:
            self._respond(400, {"error": "Thiếu API Key! Vui lòng nhập ở sidebar hoặc cấu hình biến môi trường GEMINI_API_KEY."})
            return

        message = data.get("message", "")
        model_name = data.get("model", "gemma-4-26b-a4b-it")
        system_instruction = data.get("system_instruction", "")
        history = data.get("history", [])
        enable_search = data.get("google_search", False)
        enable_functions = data.get("function_calling", False)

        try:
            client = genai.Client(api_key=api_key)

            # Xây dựng lịch sử từ frontend
            contents = build_contents(history)

            # Thêm tin nhắn mới
            if message:
                contents.append(types.Content(role="user", parts=[types.Part.from_text(text=message)]))

            # Config
            tools_list = []
            if enable_search:
                tools_list.append(types.Tool(google_search=types.GoogleSearch()))
            if enable_functions:
                tools_list.append(types.Tool(function_declarations=SAMPLE_FUNCTIONS))

            config = types.GenerateContentConfig()
            if system_instruction:
                config.system_instruction = system_instruction
            if tools_list:
                config.tools = tools_list

            # Gọi API lần 1
            response = client.models.generate_content(
                model=model_name, contents=contents, config=config
            )

            result = {"response": "", "function_calls": [], "search_sources": []}

            # Function Calling: thực thi + gọi lại model
            if response.function_calls:
                fc_list = []
                fn_response_parts = []
                for fc in response.function_calls:
                    fc_info = {"name": fc.name, "args": dict(fc.args) if fc.args else {}}
                    fc_list.append(fc_info)
                    fn_result = execute_function(fc.name, fc_info["args"])
                    fn_response_parts.append(
                        types.Part.from_function_response(name=fc.name, response={"result": fn_result})
                    )
                result["function_calls"] = fc_list

                contents.append(response.candidates[0].content)
                contents.append(types.Content(role="user", parts=fn_response_parts))

                response2 = client.models.generate_content(
                    model=model_name, contents=contents, config=config
                )
                result["response"] = response2.text or ""
            else:
                result["response"] = response.text or ""

            # Grounding metadata
            if (response.candidates and response.candidates[0].grounding_metadata
                    and response.candidates[0].grounding_metadata.grounding_chunks):
                for chunk in response.candidates[0].grounding_metadata.grounding_chunks:
                    if chunk.web:
                        result["search_sources"].append({
                            "title": chunk.web.title or "Untitled",
                            "url": chunk.web.uri or "",
                        })

            self._respond(200, result)

        except Exception as e:
            self._respond(500, {"error": str(e)})

    def _respond(self, status, data):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
