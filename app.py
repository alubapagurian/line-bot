from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os
from dotenv import load_dotenv
from sheet_helper import append_violation_record  # 匯入 Google Sheet 模組

app = Flask(__name__)
load_dotenv()

line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text.strip()

    if text.startswith("/違規"):
        parts = text.split(" ", 3)
        if len(parts) < 4:
            reply = "❗請使用正確格式：/違規 [地址] [違規類型] [描述]"
        else:
            address, violation_type, description = parts[1], parts[2], parts[3]
            append_violation(address, violation_type, description)
            reply = (f"📌 違規通報已記錄：\n"
                     f"🏠 位置：{address}\n"
                     f"🚫 類型：{violation_type}\n"
                     f"📝 描述：{description}\n"
                     f"✅ 已寫入 Google Sheet。請通知住戶限期改善。")

    elif text.startswith("/查詢"):
        keyword = text.replace("/查詢", "").strip()
        if "裝修未登記" in keyword:
            reply = ("🔍 查詢：裝修未登記\n"
                     "➡️ 立即停止施工 > 補齊手續 > 動用保證金\n"
                     "📘 依據：裝修工程申請規定、規約第17條")
        else:
            reply = "❓ 查無此違規類型，請確認關鍵字是否正確。"
    else:
        reply = "👋 請使用 /違規 或 /查詢 指令開始操作"

    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
