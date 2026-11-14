import asyncio, os, sqlite3, csv, io, html, json, hmac, hashlib
from collections import OrderedDict
from pathlib import Path
from urllib.parse import parse_qsl
from aiohttp import web
from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (Message, CallbackQuery, InlineKeyboardButton, WebAppInfo, MenuButtonWebApp,
                           KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove)
from aiogram.utils.keyboard import InlineKeyboardBuilder

TOKEN = os.environ["9024883218:AAFjDQhzemG6H6wnBpqcAD1HV2n-MKkIENo"]
BOSS = int(os.environ["8707797093"])  # boshliqning Telegram ID raqami
WEBAPP_URL = os.environ.get("https://plum-loralee-24.tiiny.site", "").rstrip("/")  # https://nomi.onrender.com
BOT = None
INDEX = Path(__file__).parent / "web" / "index.html"
PER_PAGE = 8

db = sqlite3.connect(os.environ.get("DB_PATH", "shop.db"))
db.row_factory = sqlite3.Row
db.executescript("""
create table if not exists products(id integer primary key autoincrement, cat text, name text, price integer);
create table if not exists cart(user_id integer, pid integer, qty integer, primary key(user_id, pid));
create table if not exists orders(id integer primary key autoincrement, user_id integer, name text,
  phone text, date text, total integer, created text default current_timestamp);
""")
try:
    db.execute("alter table products add column photo text")
except sqlite3.OperationalError:
    pass
db.commit()

r = Router()
is_boss = F.from_user.id == BOSS


class Order(StatesGroup):
    name = State()
    phone = State()
    date = State()
    confirm = State()


def money(n):
    return f"{int(n):,}".replace(",", " ") + " so'm"


def cats():
    return [x[0] for x in db.execute("select distinct cat from products order by cat")]


def home_kb():
    kb = InlineKeyboardBuilder()
    for i, c in enumerate(cats()):
        kb.button(text=c, callback_data=f"c:{i}:0")
    kb.adjust(2)
    if WEBAPP_URL:
        kb.row(InlineKeyboardButton(text="🛍 Do'konni ochish", web_app=WebAppInfo(url=WEBAPP_URL)))
    kb.row(InlineKeyboardButton(text="🛒 Savat", callback_data="cart"))
    return kb.as_markup()


HOME_TEXT = "🏠 Xitoy oshxona buyumlari do'koni\nBo'limni tanlang yoki mahsulot nomini yozib qidiring:"


async def show(cb: CallbackQuery, text, kb):
    if cb.message.photo:
        await cb.message.delete()
        await cb.message.answer(text, reply_markup=kb)
    else:
        await cb.message.edit_text(text, reply_markup=kb)


@r.message(CommandStart())
async def start(m: Message, state: FSMContext):
    await state.clear()
    await m.answer(HOME_TEXT, reply_markup=home_kb())


@r.callback_query(F.data == "home")
async def home(cb: CallbackQuery):
    await show(cb, HOME_TEXT, home_kb())


@r.callback_query(F.data.startswith("c:"))
async def cat_page(cb: CallbackQuery):
    _, i, p = cb.data.split(":")
    i, p = int(i), int(p)
    cat = cats()[i]
    rows = db.execute("select * from products where cat=? order by id", (cat,)).fetchall()
    kb = InlineKeyboardBuilder()
    for x in rows[p * PER_PAGE:(p + 1) * PER_PAGE]:
        kb.button(text=f"{x['name']} — {money(x['price'])}", callback_data=f"p:{x['id']}")
    kb.adjust(1)
    nav = []
    if p > 0:
        nav.append(InlineKeyboardButton(text="⬅️", callback_data=f"c:{i}:{p-1}"))
    if (p + 1) * PER_PAGE < len(rows):
        nav.append(InlineKeyboardButton(text="➡️", callback_data=f"c:{i}:{p+1}"))
    if nav:
        kb.row(*nav)
    kb.row(InlineKeyboardButton(text="🛒 Savat", callback_data="cart"),
           InlineKeyboardButton(text="🏠 Bosh sahifa", callback_data="home"))
    await cb.message.edit_text(f"📂 {cat}  ({p+1}/{max(1,-(-len(rows)//PER_PAGE))})", reply_markup=kb.as_markup())


@r.callback_query(F.data.startswith("p:"))
async def product_card(cb: CallbackQuery):
    x = db.execute("select * from products where id=?", (int(cb.data[2:]),)).fetchone()
    if not x:
        await cb.answer("Topilmadi")
        return
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="➕ Savatga qo'shish", callback_data=f"a:{x['id']}"))
    kb.row(InlineKeyboardButton(text="🛒 Savat", callback_data="cart"),
           InlineKeyboardButton(text="🏠 Bosh sahifa", callback_data="home"))
    caption = f"<b>{html.escape(x['name'])}</b>\n💰 {money(x['price'])}"
    if x["photo"]:
        await cb.message.answer_photo(x["photo"], caption=caption, reply_markup=kb.as_markup())
    else:
        await cb.message.answer(caption, reply_markup=kb.as_markup())
    await cb.answer()


@r.callback_query(F.data.startswith("a:"))
async def add(cb: CallbackQuery):
    pid = int(cb.data[2:])
    db.execute("insert into cart values(?,?,1) on conflict(user_id,pid) do update set qty=qty+1",
               (cb.from_user.id, pid))
    db.commit()
    await cb.answer("✅ Savatga qo'shildi")


def cart_rows(uid):
    return db.execute("select p.id,p.name,p.price,c.qty from cart c join products p on p.id=c.pid "
                      "where c.user_id=?", (uid,)).fetchall()


def cart_text(rows):
    lines = [f"{x['name']}\n   {x['qty']} × {money(x['price'])} = {money(x['qty']*x['price'])}" for x in rows]
    total = sum(x["qty"] * x["price"] for x in rows)
    return "\n".join(lines), total


@r.callback_query(F.data == "cart")
@r.callback_query(F.data.startswith("q:"))
async def cart(cb: CallbackQuery):
    uid = cb.from_user.id
    if cb.data.startswith("q:"):
        _, pid, d = cb.data.split(":")
        db.execute("update cart set qty=qty+? where user_id=? and pid=?", (int(d), uid, int(pid)))
        db.execute("delete from cart where qty<=0")
        db.commit()
    rows = cart_rows(uid)
    if not rows:
        await show(cb, "🛒 Savat bo'sh.", home_kb())
        return
    body, total = cart_text(rows)
    kb = InlineKeyboardBuilder()
    for x in rows:
        kb.row(InlineKeyboardButton(text="➖", callback_data=f"q:{x['id']}:-1"),
               InlineKeyboardButton(text=x["name"][:25], callback_data="noop"),
               InlineKeyboardButton(text="➕", callback_data=f"q:{x['id']}:1"))
    kb.row(InlineKeyboardButton(text="✅ Buyurtma berish", callback_data="checkout"))
    kb.row(InlineKeyboardButton(text="🗑 Tozalash", callback_data="clear"),
           InlineKeyboardButton(text="🏠 Davom etish", callback_data="home"))
    await show(cb, f"🛒 Savat\n\n{body}\n\n💰 Jami: {money(total)}", kb.as_markup())


@r.callback_query(F.data == "noop")
async def noop(cb: CallbackQuery):
    await cb.answer()


@r.callback_query(F.data == "clear")
async def clear(cb: CallbackQuery):
    db.execute("delete from cart where user_id=?", (cb.from_user.id,))
    db.commit()
    await cb.message.edit_text("🗑 Savat tozalandi.", reply_markup=home_kb())


@r.callback_query(F.data == "checkout")
async def checkout(cb: CallbackQuery, state: FSMContext):
    await state.set_state(Order.name)
    await cb.message.answer("Ismingizni yozing:")
    await cb.answer()


@r.message(Order.name)
async def got_name(m: Message, state: FSMContext):
    await state.update_data(name=m.text)
    await state.set_state(Order.phone)
    kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="📞 Raqamni yuborish", request_contact=True)]],
                             resize_keyboard=True, one_time_keyboard=True)
    await m.answer("Telefon raqamingizni yuboring yoki yozing:", reply_markup=kb)


@r.message(Order.phone)
async def got_phone(m: Message, state: FSMContext):
    phone = m.contact.phone_number if m.contact else m.text
    await state.update_data(phone=phone)
    await state.set_state(Order.date)
    await m.answer("Qaysi kunga kerak? (masalan: 20.11.2026)", reply_markup=ReplyKeyboardRemove())


@r.message(Order.date)
async def got_date(m: Message, state: FSMContext):
    await state.update_data(date=m.text)
    d = await state.get_data()
    body, total = cart_text(cart_rows(m.from_user.id))
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Tasdiqlash", callback_data="ok")
    kb.button(text="❌ Bekor qilish", callback_data="cancel")
    await state.set_state(Order.confirm)
    await m.answer(f"👤 {d['name']}\n📞 {d['phone']}\n📅 {d['date']}\n\n{body}\n\n💰 Jami: {money(total)}",
                   reply_markup=kb.as_markup())


@r.callback_query(F.data == "cancel")
async def cancel(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await cb.message.edit_text("Bekor qilindi.", reply_markup=home_kb())


@r.callback_query(F.data == "ok", Order.confirm)
async def confirm(cb: CallbackQuery, state: FSMContext, bot: Bot):
    d = await state.get_data()
    uid = cb.from_user.id
    rows = cart_rows(uid)
    body, total = cart_text(rows)
    cur = db.execute("insert into orders(user_id,name,phone,date,total) values(?,?,?,?,?)",
                     (uid, d["name"], d["phone"], d["date"], total))
    db.execute("delete from cart where user_id=?", (uid,))
    db.commit()
    oid = cur.lastrowid
    await bot.send_message(
        BOSS,
        f"🆕 <b>Yangi buyurtma #{oid}</b>\n"
        f"👤 <a href=\"tg://user?id={uid}\">{html.escape(d['name'])}</a>\n"
        f"📞 {html.escape(d['phone'])}\n📅 {html.escape(d['date'])}\n\n"
        f"{html.escape(body)}\n\n💰 Jami: <b>{money(total)}</b>")
    await state.clear()
    await cb.message.edit_text(f"✅ Buyurtma #{oid} qabul qilindi! Tez orada bog'lanamiz.")


# ---------- Boshliq buyruqlari ----------
@r.message(Command("admin"), is_boss)
async def admin_help(m: Message):
    await m.answer(
        "<b>Boshliq buyruqlari</b>\n"
        "/find so'z — mahsulot ID sini topish\n"
        "/price ID narx — narxni o'zgartirish\n"
        "/add Bo'lim | Nomi | Narx — mahsulot qo'shish\n"
        "/del ID — o'chirish\n"
        "/orders — oxirgi 10 buyurtma\n"
        "📷 Rasm biriktirish: rasm yuboring, tagiga tovar ID sini yozing\n"
        "CSV fayl yuboring (ustunlar: bo'lim,nomi,narx) — ko'p mahsulotni birdan yuklash")


@r.message(Command("find"), is_boss)
async def find(m: Message):
    q = m.text.partition(" ")[2].strip()
    rows = db.execute("select * from products where name like ? limit 20", (f"%{q}%",)).fetchall()
    await m.answer("\n".join(f"#{x['id']} {x['name']} — {money(x['price'])}" for x in rows) or "Topilmadi")


@r.message(Command("price"), is_boss)
async def price(m: Message):
    try:
        _, pid, new = m.text.split()
        db.execute("update products set price=? where id=?", (int(new), int(pid)))
        db.commit()
        await m.answer("✅ Narx o'zgartirildi")
    except Exception:
        await m.answer("Format: /price 15 25000")


@r.message(Command("add"), is_boss)
async def add_product(m: Message):
    try:
        cat, name, p = [s.strip() for s in m.text.partition(" ")[2].split("|")]
        db.execute("insert into products(cat,name,price) values(?,?,?)", (cat, name, int(p)))
        db.commit()
        await m.answer("✅ Qo'shildi")
    except Exception:
        await m.answer("Format: /add Idishlar | Piyola | 12000")


@r.message(Command("del"), is_boss)
async def delete(m: Message):
    try:
        db.execute("delete from products where id=?", (int(m.text.split()[1]),))
        db.commit()
        await m.answer("🗑 O'chirildi")
    except Exception:
        await m.answer("Format: /del 15")


@r.message(Command("orders"), is_boss)
async def orders(m: Message):
    rows = db.execute("select * from orders order by id desc limit 10").fetchall()
    await m.answer("\n".join(f"#{x['id']} {x['name']} {x['phone']} {x['date']} — {money(x['total'])}"
                             for x in rows) or "Buyurtma yo'q")


@r.message(F.photo, is_boss)
async def set_photo(m: Message):
    cap = (m.caption or "").strip()
    if not cap.isdigit():
        await m.answer("Rasm tagiga faqat tovar ID sini yozib yuboring. Masalan: 15")
        return
    cur = db.execute("update products set photo=? where id=?", (m.photo[-1].file_id, int(cap)))
    db.commit()
    await m.answer("✅ Rasm biriktirildi" if cur.rowcount else "Bunday ID topilmadi")


@r.message(F.document, is_boss)
async def import_csv(m: Message, bot: Bot):
    buf = io.BytesIO()
    await bot.download(m.document, destination=buf)
    text = buf.getvalue().decode("utf-8-sig")
    n = 0
    for row in csv.reader(io.StringIO(text)):
        try:
            db.execute("insert into products(cat,name,price) values(?,?,?)",
                       (row[0].strip(), row[1].strip(), int(row[2])))
            n += 1
        except Exception:
            continue
    db.commit()
    await m.answer(f"✅ {n} ta mahsulot yuklandi")


# ---------- Qidiruv ----------
@r.message(StateFilter(None), F.text, ~F.text.startswith("/"))
async def search(m: Message):
    rows = db.execute("select * from products where name like ? limit 15", (f"%{m.text}%",)).fetchall()
    if not rows:
        await m.answer("Topilmadi. Boshqa nom yozing.", reply_markup=home_kb())
        return
    kb = InlineKeyboardBuilder()
    for x in rows:
        kb.button(text=f"{x['name']} — {money(x['price'])}", callback_data=f"p:{x['id']}")
    kb.adjust(1)
    kb.row(InlineKeyboardButton(text="🛒 Savat", callback_data="cart"))
    await m.answer("🔎 Natijalar:", reply_markup=kb.as_markup())


# ---------- Mini App (veb) ----------
def check_init(init_data):
    """Telegram initData imzosini tekshiradi, foydalanuvchini qaytaradi."""
    try:
        data = dict(parse_qsl(init_data, keep_blank_values=True))
        got = data.pop("hash", "")
        check = "\n".join(f"{k}={v}" for k, v in sorted(data.items()))
        secret = hmac.new(b"WebAppData", TOKEN.encode(), hashlib.sha256).digest()
        calc = hmac.new(secret, check.encode(), hashlib.sha256).hexdigest()
        if got and hmac.compare_digest(calc, got):
            return json.loads(data["user"])
    except Exception:
        pass
    return None


def err(msg, status=400):
    return web.json_response({"error": msg}, status=status)


async def page(req):
    return web.FileResponse(INDEX)


async def api_products(req):
    rows = db.execute("select id,cat,name,price,photo from products order by cat,id").fetchall()
    out = [{"i": x["id"], "c": x["cat"], "n": x["name"], "p": x["price"],
            "h": hashlib.md5(x["photo"].encode()).hexdigest()[:8] if x["photo"] else ""} for x in rows]
    return web.json_response(out, headers={"Cache-Control": "no-cache"})


async def api_me(req):
    u = check_init(req.headers.get("X-Init", ""))
    return web.json_response({"boss": bool(u and u["id"] == BOSS)})


PHOTOS = OrderedDict()


async def photo(req):
    row = db.execute("select photo from products where id=?", (int(req.match_info["id"]),)).fetchone()
    if not row or not row["photo"]:
        raise web.HTTPNotFound()
    fid = row["photo"]
    if fid not in PHOTOS:
        f = await BOT.get_file(fid)
        buf = io.BytesIO()
        await BOT.download_file(f.file_path, buf)
        PHOTOS[fid] = buf.getvalue()
        if len(PHOTOS) > 120:
            PHOTOS.popitem(last=False)
    return web.Response(body=PHOTOS[fid], content_type="image/jpeg",
                        headers={"Cache-Control": "public, max-age=604800"})


async def api_price(req):
    try:
        d = await req.json()
        u = check_init(d.get("init", ""))
        if not u or u["id"] != BOSS:
            return err("Ruxsat yo'q", 403)
        db.execute("update products set price=? where id=?", (int(d["price"]), int(d["id"])))
        db.commit()
        return web.json_response({"ok": True})
    except (ValueError, KeyError, TypeError):
        return err("Noto'g'ri so'rov")


async def api_order(req):
    try:
        d = await req.json()
        u = check_init(d.get("init", ""))
        if not u:
            return err("Do'konni Telegram ichida oching", 401)
        lines, total = [], 0
        for it in d.get("items") or []:
            row = db.execute("select * from products where id=?", (int(it["id"]),)).fetchone()
            qty = int(it["qty"])
            if row and 0 < qty <= 999:
                lines.append(f"{row['name']}\n   {qty} × {money(row['price'])} = {money(qty * row['price'])}")
                total += qty * row["price"]
        name = str(d.get("name", "")).strip()[:60]
        phone = str(d.get("phone", "")).strip()[:30]
        date = str(d.get("date", "")).strip()[:20]
    except (ValueError, KeyError, TypeError):
        return err("Noto'g'ri so'rov")
    if not (lines and name and phone and date):
        return err("Ism, telefon, sana va mahsulotlar kerak")
    cur = db.execute("insert into orders(user_id,name,phone,date,total) values(?,?,?,?,?)",
                     (u["id"], name, phone, date, total))
    db.commit()
    oid = cur.lastrowid
    body = "\n".join(lines)
    await BOT.send_message(
        BOSS,
        f"🆕 <b>Yangi buyurtma #{oid}</b> (do'kon)\n"
        f"👤 <a href=\"tg://user?id={u['id']}\">{html.escape(name)}</a>\n"
        f"📞 {html.escape(phone)}\n📅 {html.escape(date)}\n\n"
        f"{html.escape(body)}\n\n💰 Jami: <b>{money(total)}</b>")
    try:
        await BOT.send_message(u["id"], f"✅ Buyurtma #{oid} qabul qilindi. Jami: {money(total)}")
    except Exception:
        pass
    return web.json_response({"id": oid, "total": total})


async def main():
    global BOT
    BOT = Bot(TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
    app = web.Application()
    app.add_routes([web.get("/", page), web.get("/api/products", api_products), web.get("/api/me", api_me),
                    web.get(r"/photo/{id:\d+}", photo), web.post("/api/price", api_price),
                    web.post("/api/order", api_order)])
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", int(os.environ.get("PORT", 8080))).start()
    if WEBAPP_URL:
        await BOT.set_chat_menu_button(menu_button=MenuButtonWebApp(text="Do'kon", web_app=WebAppInfo(url=WEBAPP_URL)))
    dp = Dispatcher()
    dp.include_router(r)
    await dp.start_polling(BOT)


if __name__ == "__main__":
    asyncio.run(main())
