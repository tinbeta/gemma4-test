import os
import json
import math
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

app = Flask(__name__, static_folder='public', static_url_path='')
CORS(app)

# Giới hạn kích thước payload (Vercel limit ~4.5MB, để 4MB cho an toàn)
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024

@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({"error": "File quá lớn! Vercel giới hạn tối đa 4MB bộ nhớ đệm. Vui lòng chọn ảnh nhỏ hơn."}), 413

client = genai.Client(api_key=api_key)

# Lịch sử hội thoại sẽ được truyền từ frontend lên,
# không lưu bằng global state nữa để hỗ trợ Serverless (Vercel)
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
    """Thực thi hàm mẫu và trả về kết quả giả lập."""
    if name == "get_weather":
        loc = args.get("location", "Unknown")
        return json.dumps({
            "location": loc,
            "temperature": "28°C",
            "condition": "Có mây, khả năng mưa rào buổi chiều",
            "humidity": "75%",
            "wind": "Gió nhẹ 12 km/h hướng Đông Nam",
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
                {"name": f"Hanoi La Siesta - {city}", "rating": 4.5, "price": "$$$"},
            ],
            "cafe": [
                {"name": f"Cộng Cà Phê - {city}", "rating": 4.4, "price": "$"},
                {"name": f"The Note Coffee - {city}", "rating": 4.2, "price": "$"},
                {"name": f"Loading T Cafe - {city}", "rating": 4.3, "price": "$$"},
            ],
            "attraction": [
                {"name": f"Hoàn Kiếm Lake - {city}", "rating": 4.7, "price": "Free"},
                {"name": f"Old Quarter - {city}", "rating": 4.6, "price": "Free"},
                {"name": f"Temple of Literature - {city}", "rating": 4.5, "price": "$"},
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
    else:
        return json.dumps({"error": f"Unknown function: {name}"})


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/send", methods=["POST"])
@app.route("/api/send", methods=["POST"])
def send_message():
    message = request.form.get("message", "")
    model_name = request.form.get("model", "gemma-4-26b-a4b-it")
    system_instruction = request.form.get("system_instruction", "")
    image_file = request.files.get("image")
    enable_search = request.form.get("google_search", "false") == "true"
    enable_functions = request.form.get("function_calling", "false") == "true"
    custom_api_key = request.form.get("api_key", "").strip()

    # Sử dụng API key tùy chỉnh nếu có, nếu không thì dùng key mặc định
    active_client = client
    if custom_api_key:
        active_client = genai.Client(api_key=custom_api_key)

    # --- ĐỌC LỊCH SỬ TỪ FRONTEND ---
    history_str = request.form.get("history", "[]")
    conversation_history = []
    try:
        history_data = json.loads(history_str)
        for item in history_data:
            role = item.get("role")
            # Chỉ nạp lại các tin nhắn chữ để tiết kiệm Payload (bỏ qua ảnh cũ)
            parts = [types.Part.from_text(text=p.get("text", "")) for p in item.get("parts", []) if "text" in p]
            if parts:
                conversation_history.append(types.Content(role=role, parts=parts))
    except Exception as e:
        print(f"Error parsing history: {e}")

    # Xử lý tin nhắn và ảnh hiện tại
    try:
        user_parts = []
        if image_file:
            image_bytes = image_file.read()
            mime_type = image_file.content_type
            user_parts.append(types.Part.from_bytes(data=image_bytes, mime_type=mime_type))
        if message:
            user_parts.append(types.Part.from_text(text=message))

        if not user_parts:
            return jsonify({"error": "No content provided"}), 400

        conversation_history.append(types.Content(role="user", parts=user_parts))

        # Config
        tools_list = []
        if enable_search:
            tools_list.append(types.Tool(google_search=types.GoogleSearch()))
        if enable_functions:
            tools_list.append(types.Tool(function_declarations=SAMPLE_FUNCTIONS))

        # Chỉ dẫn hệ thống mặc định để tối ưu hóa việc dùng Tool (giúp tiết kiệm thời gian)
        BASE_SYSTEM = (
            "Bạn là trợ lý AI chuyên nghiệp. "
            "Nếu Google Search được bật, CHỈ SỬ DỤNG nó khi câu hỏi của người dùng thực sự cần thông tin mới nhất, tin tức thời sự hoặc dữ liệu thực tế mà bạn không biết chắc chắn. "
            "Với các câu chào hỏi, thảo luận chung hoặc kiến thức phổ thông, hãy trả lời trực tiếp ngay lập tức."
        )

        config = types.GenerateContentConfig()
        combined_sys = BASE_SYSTEM
        if system_instruction:
            combined_sys += "\n\nChỉ dẫn bổ sung từ người dùng:\n" + system_instruction
        
        config.system_instruction = combined_sys
        if tools_list:
            config.tools = tools_list

        # Gửi yêu cầu lần 1
        response = active_client.models.generate_content(
            model=model_name,
            contents=conversation_history,
            config=config,
        )

        result = {"response": "", "function_calls": [], "search_sources": []}

        # Nếu model muốn gọi hàm → thực thi → gửi lại kết quả cho model
        if response.function_calls:
            fc_list = []
            fn_response_parts = []

            for fc in response.function_calls:
                fc_info = {"name": fc.name, "args": dict(fc.args) if fc.args else {}}
                fc_list.append(fc_info)

                # Thực thi hàm
                fn_result = execute_function(fc.name, fc_info["args"])
                fn_response_parts.append(
                    types.Part.from_function_response(name=fc.name, response={"result": fn_result})
                )

            result["function_calls"] = fc_list

            # Lưu phản hồi function call của model vào lịch sử
            conversation_history.append(response.candidates[0].content)

            # Gửi kết quả hàm ngược lại cho model
            conversation_history.append(types.Content(role="user", parts=fn_response_parts))

            # Gọi model lần 2 để tổng hợp câu trả lời từ kết quả hàm
            response2 = active_client.models.generate_content(
                model=model_name,
                contents=conversation_history,
                config=config,
            )

            final_text = response2.text or ""
            result["response"] = final_text
            conversation_history.append(
                types.Content(role="model", parts=[types.Part.from_text(text=final_text)])
            )
        else:
            text = response.text or ""
            result["response"] = text
            conversation_history.append(
                types.Content(role="model", parts=[types.Part.from_text(text=text)])
            )

        # Grounding metadata
        if (
            response.candidates
            and response.candidates[0].grounding_metadata
            and response.candidates[0].grounding_metadata.grounding_chunks
        ):
            for chunk in response.candidates[0].grounding_metadata.grounding_chunks:
                if chunk.web:
                    result["search_sources"].append({
                        "title": chunk.web.title or "Untitled",
                        "url": chunk.web.uri or "",
                    })

        return jsonify(result)

    except Exception as e:
        if conversation_history and conversation_history[-1].role == "user":
            conversation_history.pop()
        return jsonify({"error": str(e)}), 500


@app.route("/clear", methods=["POST"])
def clear():
    # Stateless backend không cần quản lý lịch sử
    return jsonify({"status": "cleared"})


if __name__ == "__main__":
    app.run(debug=True, port=5001)
