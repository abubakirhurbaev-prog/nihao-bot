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
CHANNEL = "@nihai_uqu"
CHANNEL_LINK = "https://t.me/nihai_uqu"

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
<!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Xitoy Oshxona Tovarlari Do'koni</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        body { font-family: Arial, sans-serif; background: #f4f4f9; margin: 0; padding: 10px; color: #333; }
        h1 { text-align: center; font-size: 20px; color: #ff4757; }
        .product-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; padding-bottom: 80px; }
        .product-card { background: #fff; padding: 10px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); text-align: center; }
        .product-card img { width: 100%; height: 100px; object-fit: cover; border-radius: 5px; }
        .product-card h3 { font-size: 14px; margin: 8px 0; }
        .product-card p { color: #2ed573; font-weight: bold; font-size: 14px; }
        .product-card button { background: #ff4757; color: white; border: none; padding: 5px 10px; border-radius: 5px; cursor: pointer; }
        
        /* Savatcha paneli */
        .cart-bar { position: fixed; bottom: 0; left: 0; right: 0; background: #fff; padding: 10px 15px; box-shadow: 0 -2px 10px rgba(0,0,0,0.1); display: flex; justify-content: space-between; align-items: center; border-top: 1px solid #ddd; }
        .cart-bar button { background: #2ed573; color: white; border: none; padding: 10px 20px; border-radius: 5px; font-weight: bold; cursor: pointer; }
        
        /* Modal oyna (Buyurtma berish) */
        .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); justify-content: center; align-items: center; }
        .modal-content { background: #fff; padding: 20px; border-radius: 10px; width: 90%; max-width: 400px; }
        .modal-content input { width: 100%; padding: 8px; margin: 8px 0; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }
        .modal-content button { width: 100%; background: #2ed573; color: white; border: none; padding: 10px; border-radius: 5px; font-weight: bold; cursor: pointer; margin-top: 10px; }
    </style>
</head>
<body>

    <h1>🇨🇳 Xitoy Oshxona Tovarlari</h1>
    
    <div class="product-grid" id="product-list">
        <!-- Tovarlar shu yerda chiqadi -->
    </div>

    <!-- Savatcha paneli -->
    <div class="cart-bar">
        <div>Jami: <span id="total-price">0</span> so'm</div>
        <button onclick="openModal()">Buyurtma berish 🛒</button>
    </div>

    <!-- Ma'lumot kiritish oynasi -->
    <div class="modal" id="orderModal">
        <div class="modal-content">
            <h3>Ma'lumotlaringizni kiriting</h3>
            <input type="text" id="name" placeholder="Ismingiz">
            <input type="tel" id="phone" placeholder="Telefon raqamingiz (+998...)">
            <input type="text" id="address" placeholder="Yetkazib berish manzili">
            <button onclick="checkout()">Tasdiqlash va Yuborish</button>
            <button style="background:#ccc; margin-top:5px;" onclick="closeModal()">Yopish</button>
        </div>
    </div>

    <script>
        const tg = window.Telegram.WebApp;
        tg.expand();

        // Xitoy oshxona tovarlari ro'yxati (xohlasangiz 1100 tagacha ko'paytirishingiz mumkin)
        const products = [
            { id: 1, name: "Zanglamaydigan pichoq", price: 45000, img: "https://via.placeholder.com/150" },
            { id: 2, name: "Oshxona tarozisi", price: 85000, img: "https://via.placeholder.com/150" },
            { id: 3, name: "Silikon idish qoshiq", price: 25000, img: "https://via.placeholder.com/150" },
            { id: 4, name: "Sabzavot to'g'ragich", price: 120000, img: "https://via.placeholder.com/150" }
        ];

        let cart = {};

        function renderProducts() {
            const list = document.getElementById('product-list');
            list.innerHTML = products.map(p => `
                <div class="product-card">
                    <img src="${p.img}" alt="${p.name}">
                    <h3>${p.name}</h3>
                    <p>${p.price.toLocaleString()} so'm</p>
                    <button onclick="addToCart(${p.id})">Qo'shish</button>
                </div>
            `).join('');
        }

        function addToCart(id) {
            cart[id] = (cart[id] || 0) + 1;
            updateCart();
        }

        function updateCart() {
            let total = 0;
            for (let id in cart) {
                let p = products.find(item => item.id == id);
                total += p.price * cart[id];
            }
            document.getElementById('total-price').innerText = total.toLocaleString();
        }

        function openModal() {
            if (Object.keys(cart).length === 0) {
                alert("Savatchangiz bo'sh!");
                return;
            }
            document.getElementById('orderModal').style.display = 'flex';
        }

        function closeModal() {
            document.getElementById('orderModal').style.display = 'none';
        }

        function checkout() {
            let name = document.getElementById('name').value;
            let phone = document.getElementById('phone').value;
            let address = document.getElementById('address').value;

            if (!name || !phone || !address) {
                alert("Iltimos, barcha maydonlarni to'ldiring!");
                return;
            }

            let orderData = "📦 Yangi buyurtma:\n\n";
            let totalPrice = 0;

            for (let id in cart) {
                let p = products.find(item => item.id == id);
                orderData += `- ${p.name} x ${cart[id]} ta = ${(p.price * cart[id]).toLocaleString()} so'm\n`;
                totalPrice += p.price * cart[id];
            }

            orderData += `\n💰 Jami summa: ${totalPrice.toLocaleString()} so'm`;
            orderData += `\n👤 Mijoz: ${name}\n📞 Tel: ${phone}\n📍 Manzil: ${address}`;

            // Buyurtmani botingizga yuborish
            tg.sendData(orderData);
            tg.close();
        }

        renderProducts();
    </script>
</body>
</html>
