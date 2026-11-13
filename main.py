import json
import ssl
import time
import urllib.parse
import urllib.request

# SSL xatoligini chetlab o'tish
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

TOKEN = "9024883218:AAFjDQhzemG6H6wnBpqcAD1HV2n-MKkIENo"
GAME_URL = "https://dapper-gumption-5f4e6c.netlify.app/"
CHANNEL = "@Nihaooquvmarkazi"
CHANNEL_LINK = "https://t.me/Nihaooquvmarkazi"

API_URL = f"https://api.telegram.org/bot{TOKEN}/"


def api_call(method, params=None):
  url = API_URL + method
  if params:
    data = urllib.parse.urlencode(params).encode("utf-8")
    req = urllib.request.Request(url, data=data)
  else:
    req = urllib.request.Request(url)
  try:
    with urllib.request.urlopen(req, timeout=30, context=ctx) as resp:
      return json.loads(resp.read().decode("utf-8"))
  except Exception as e:
    print("API Xatolik:", e)
    return None


def is_subscribed(user_id):
  res = api_call("getChatMember", {"chat_id": CHANNEL, "user_id": user_id})
  if res and res.get("ok"):
    status = res["result"]["status"]
    return status in ["member", "administrator", "creator"]
  return False


def send_message(chat_id, text, reply_markup=None):
  params = {"chat_id": chat_id, "text": text}
  if reply_markup:
    params["reply_markup"] = json.dumps(reply_markup)
  api_call("sendMessage", params)


def edit_message(chat_id, message_id, text, reply_markup=None):
  params = {"chat_id": chat_id, "message_id": message_id, "text": text}
  if reply_markup:
    params["reply_markup"] = json.dumps(reply_markup)
  api_call("editMessageText", params)


def answer_callback(callback_id, text, show_alert=False):
  api_call(
      "answerCallbackQuery",
      {
          "callback_query_id": callback_id,
          "text": text,
          "show_alert": show_alert,
      },
  )


subscribe_kb = {
    "inline_keyboard": [
        [{"text": "📢 Kanalga obuna bo‘lish", "url": CHANNEL_LINK}],
        [{"text": "Tekshirish ✅", "callback_data": "check"}],
    ]
}

play_kb = {
    "inline_keyboard": [
        [{"text": "O‘ynash 🎮", "web_app": {"url": GAME_URL}}]
    ]
}


def main():
  print("Bot muvaffaqiyatli ishga tushdi!")
  offset = 0
  while True:
    updates = api_call("getUpdates", {"offset": offset, "timeout": 20})
    if updates and updates.get("ok"):
      for item in updates["result"]:
        offset = item["update_id"] + 1

        if "message" in item and "text" in item["message"]:
          msg = item["message"]
          chat_id = msg["chat"]["id"]
          user_id = msg["from"]["id"]
          if msg["text"] == "/start":
            if is_subscribed(user_id):
              send_message(
                  chat_id,
                  "你好! 🐼 Xitoycha so‘z o‘yiniga xush kelibsiz!",
                  play_kb,
              )
            else:
              send_message(
                  chat_id,
                  "你好! 🐼 O‘yinni ochish uchun avval NIHAO o‘quv markazi"
                  " kanaliga obuna bo‘ling, keyin «Tekshirish» tugmasini"
                  " bosing.",
                  subscribe_kb,
              )

        elif "callback_query" in item:
          cb = item["callback_query"]
          user_id = cb["from"]["id"]
          chat_id = cb["message"]["chat"]["id"]
          msg_id = cb["message"]["message_id"]
          if cb["data"] == "check":
            if is_subscribed(user_id):
              answer_callback(cb["id"], "Barakalla! 🎉")
              edit_message(
                  chat_id,
                  msg_id,
                  "Obuna tasdiqlandi ✅ Endi o‘ynashingiz mumkin!",
                  play_kb,
              )
            else:
              answer_callback(
                  cb["id"], "Hali obuna bo‘lmadingiz ❌", show_alert=True
              )
    time.sleep(0.5)


if __name__ == "__main__":
  main()
