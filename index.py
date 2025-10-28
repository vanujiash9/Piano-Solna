# File: api/index.py

from flask import Flask, request, jsonify
import requests
import os  # Sử dụng thư viện os mặc định


app = Flask(__name__)

ZALO_ACCESS_TOKEN = os.environ.get("ZALO_ACCESS_TOKEN")

get_gemini_response = None
try:
    # register blueprint nếu có
    from chat import register_to_app
    register_to_app(app)
except Exception:
    pass

try:
    from chat import get_gemini_response as _ggr
    get_gemini_response = _ggr
except Exception:
    # fallback: hàm trả lời đơn giản
    def get_gemini_response(text):
        return '(Trả lời tạm thời) ' + str(text)

@app.route("/webhook", methods=["POST"])
def webhook():
    # --- THAY ĐỔI 2: Thêm một dòng kiểm tra token để đảm bảo token đã được nạp ---
    if not ZALO_ACCESS_TOKEN:
        print("LỖI: Biến môi trường ZALO_ACCESS_TOKEN chưa được cài đặt!")
        return jsonify({"status": "error", "message": "Server configuration error"}), 500

    data = request.get_json()
    print("Zalo gửi:", data)

    message = data.get("message", {}).get("text", "")
    user_id = data.get("sender", {}).get("id", "")

    if not message or not user_id:
        return jsonify({"status": "ignored"})

    reply = get_gemini_response(message)
    send_message_to_zalo(user_id, reply)
    return jsonify({"status": "ok"})


@app.route('/', methods=['GET'])
def index():
    return (
        "PianoSolnaBot running on Vercel. Use POST /webhook for Zalo callbacks."
    )


@app.route('/routes', methods=['GET'])
def list_routes():
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append({'endpoint': rule.endpoint, 'rule': str(rule), 'methods': list(rule.methods)})
    return jsonify({'routes': routes})

def send_message_to_zalo(user_id, text):
    url = "https://openapi.zalo.me/v3.0/oa/message/callback"
    headers = {
        "Content-Type": "application/json",
        "access_token": ZALO_ACCESS_TOKEN
    }
    payload = {
        "recipient": {"user_id": user_id},
        "message": {"text": text}
    }
    print(f"Đang gửi đến Zalo cho user {user_id}: {text}")
    response = requests.post(url, json=payload, headers=headers)
    print(f"Phản hồi từ Zalo API: {response.status_code} - {response.text}")

