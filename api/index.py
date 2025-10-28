# File: api/index.py

from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

ZALO_ACCESS_TOKEN = os.environ.get("ZALO_ACCESS_TOKEN")

# Hàm trả lời đơn giản để test
def get_gemini_response(text):
    return f"Bạn vừa nói: {text}"

# -------------------------------------------------------------------
# ĐÂY LÀ ROUTE QUAN TRỌNG NHẤT MÀ ZALO CẦN
# -------------------------------------------------------------------
@app.route("/webhook", methods=["POST"])
def zalo_webhook():
    # In ra terminal của Vercel để bạn có thể xem log
    print("=== Webhook đã được Zalo gọi! ===")
    
    if not ZALO_ACCESS_TOKEN:
        print("LỖI: Biến môi trường ZALO_ACCESS_TOKEN chưa được cài đặt trên Vercel!")
        return jsonify({"status": "error", "message": "Server configuration error"}), 500

    data = request.get_json()
    print("Dữ liệu Zalo gửi:", data)

    # Xử lý tin nhắn (giữ nguyên code của bạn)
    message = data.get("message", {}).get("text", "")
    user_id = data.get("sender", {}).get("id", "")

    if not message or not user_id:
        return jsonify({"status": "ignored"})

    reply = get_gemini_response(message)
    send_message_to_zalo(user_id, reply)
    
    # Trả về status 200 OK cho Zalo
    return jsonify({"status": "ok"})
# -------------------------------------------------------------------

# Route mặc định để kiểm tra xem web có chạy không
@app.route('/', methods=['GET'])
def index():
    return "PianoSolnaBot is running on Vercel. Webhook is at /webhook."

# Hàm gửi tin nhắn (giữ nguyên)
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
    response = requests.post(url, json=payload, headers=headers)
    print(f"Phản hồi từ Zalo API: {response.status_code}")
