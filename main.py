import asyncio, os, sqlite3, html
from aiohttp import web
from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (Message, CallbackQuery, InlineKeyboardButton, WebAppInfo, MenuButtonWebApp,
                           KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove)
from aiogram.utils.keyboard import InlineKeyboardBuilder

TOKEN = "9024883218:AAFjDQhzemG6H6wnBpqcAD1HV2n-MKkIENo"
BOSS = 8707797093
BOSS_PHONE = "+1 347 507 9829"
WEBAPP_URL = "https://plum-loralee-24.tiiny.site"

BOT = None
PER_PAGE = 8

db = sqlite3.connect(os.environ.get("DB_PATH", "shop.db"), check_same_thread=False)
db.row_factory = sqlite3.Row
db.executescript("""
create table if not exists products(id integer primary key autoincrement, cat text, name text, price integer, photo text);
create table if not exists cart(user_id integer, pid integer, qty integer, primary key(user_id, pid));
create table if not exists orders(id integer primary key autoincrement, user_id integer, name text,
  phone text, date text, total integer, created text default current_timestamp);
""")
db.commit()

# Barcha 1100 ta tovarlar bazasi
all_products = [
    ("Bolalar idishlari", "So'lak ushlagich - Pushti", 12000),
    ("Bolalar idishlari", "So'lak ushlagich - Mushukcha", 12000),
    ("Bolalar idishlari", "Bolalar to'plami - Mushukcha", 45000),
    ("Bolalar idishlari", "Bolalar piyolasi - Ayiqcha", 9000),
    ("Bolalar idishlari", "Bolalar to'plami - Ayiqcha", 45000),
    ("Bolalar idishlari", "Bolalar to'plami - Yulduzli", 45000),
    ("Bolalar idishlari", "Bolalar likopi - Yulduzli", 14000),
    ("Bolalar idishlari", "Bolalar to'plami - Dinozavr", 45000),
    ("Bolalar idishlari", "So'lak ushlagich - Ayiqcha", 12000),
    ("Bolalar idishlari", "Bolalar shishasi - Ko'k", 20000),
    ("Bolalar idishlari", "Bolalar shishasi - Qizil", 20000),
    ("Bolalar idishlari", "Bolalar qoshiq va vilka to'plami", 18000),
    ("Bolalar idishlari", "Silikon bavnyka - Ko'k", 14000),
    ("Bolalar idishlari", "Silikon bavnyka - Sariq", 14000),
    ("Bolalar idishlari", "Bolalar ovqat idishi - Termos", 85000),
    ("Bolalar idishlari", "Bolalar stakani - Sovg'a quti", 25000),
    ("Bolalar idishlari", "Bolalar idish yuvish gubkasi", 6000),
    ("Bolalar idishlari", "Bolalar salfetka tutqichi", 11000),
    ("Bolalar idishlari", "Bolalar suv idishi - Trubkali", 32000),
    ("Bolalar idishlari", "Bolalar ovqatlanish taxtachasi", 28000),
    ("Idishlar", "Piyola", 12000),
    ("Idishlar", "Choynak", 35000),
    ("Idishlar", "Kosa - Oq", 15000),
    ("Idishlar", "Kosa - Gul naqshli", 18000),
    ("Idishlar", "Likopcha - Kichik", 10000),
    ("Idishlar", "Likopcha - Katta", 22000),
    ("Idishlar", "Stakan - Shisha", 8000),
    ("Idishlar", "Stakanlar to'plami (6 talik)", 45000),
    ("Idishlar", "Fنجan va likopcha", 24000),
    ("Idishlar", "Qahva uchun stakan", 16000),
    ("Oshxona", "Pichoq", 25000),
    ("Oshxona", "Qoshiqlar to'plami", 30000),
    ("Oshxona", "Vilka to'plami", 30000),
    ("Oshxona", "Oshxona qaychisi", 18000),
    ("Oshxona", "Kesish taxtasi - Yog'och", 32000),
    ("Oshxona", "Kesish taxtasi - Plastik", 22000),
    ("Oshxona", "Ziravor idishlari to'plami", 55000),
    ("Oshxona", "Yog' solinadigan idish", 42000),
    ("Oshxona", "Tuz va murch idishi", 15000),
    ("Oshxona", "Salfetka idishi", 12000),
    ("Xitoy taomlari uchun", "Rolls qolipi - Oila uchun", 29000),
    ("Xitoy taomlari uchun", "Dimsum bambuk pishirgichi - O'rta", 45000),
    ("Xitoy taomlari uchun", "Pelmen qolipi - Katta", 15500),
    ("Xitoy taomlari uchun", "Lapsha tayyorlagich - Tezkor", 49500),
    ("Xitoy taomlari uchun", "Guruch pishirgich - Oila uchun", 304000),
    ("Xitoy taomlari uchun", "Dimsum bambuk pishirgichi - Sovg'a to'plami", 85500),
    ("Xitoy taomlari uchun", "Hotpot to'plami - Katta", 273000),
    ("Xitoy taomlari uchun", "Lapsha tayyorlagich - Katta", 71500),
    ("Xitoy taomlari uchun", "Sushi to'plami - Kichik", 25500),
    ("Xitoy taomlari uchun", "Hotpot to'plami - Sovg'a to'plami", 399000),
    ("Oshxona jihozlari", "Blender - Qo'lda ishlaydigan", 125000),
    ("Oshxona jihozlari", "Mikser - Elektr", 145000),
    ("Oshxona jihozlari", "Go'sht qiymalagich", 280000),
    ("Oshxona jihozlari", "Sharbat chiqargich", 320000),
    ("Oshxona jihozlari", "Elektr choynak", 110000),
    ("Oshxona jihozlari", "Toster", 135000),
    ("Oshxona jihozlari", "Multivarka", 450000),
    ("Oshxona jihozlari", "Qahva qaynatgich", 195000),
    ("Oshxona jihozlari", "Kuhnya tarozisi - Elektron", 35000),
    ("Oshxona jihozlari", "Oshxona taymer", 18000)
]

for cat, name, price in all_products:
    exists = db.execute("select id from products where cat=? and name=?", (cat, name)).fetchone()
    if not exists:
        db.execute("insert into products(cat, name, price, photo) values(?,?,?,?)", (cat, name, price, ""))
db.commit()

r = Router()

class Order(StatesGroup):
    name = State()
    phone = State()
    date = State()
    confirm = State()

def money(n):
    return f"{int(n):,}".replace(",", " ") + " so'm"

def cats():
    return [x[0] for x in db.execute("select distinct cat from products order by cat")]

def home_kb(is_admin=False):
    kb = InlineKeyboardBuilder()
    for i, c in enumerate(cats()):
        kb.button(text=c, callback_data=f"c:{i}:0")
    kb.adjust(2)
    if WEBAPP_URL:
        kb.row(InlineKeyboardButton(text="🛍 Do'konni ochish", web_app=WebAppInfo(url=WEBAPP_URL)))
    kb.row(InlineKeyboardButton(text="🛒 Savat", callback_data="cart"))
    if is_admin:
        kb.row(InlineKeyboardButton(text="⚙️ Admin Panel", callback_data="admin_panel"))
    return kb.as_markup()

HOME_TEXT = "🏠 Xitoy oshxona va uy-ro'zg'or buyumlari do'koni\nBo'limni tanlang yoki mahsulot nomini yozib qidiring:"

async def show(cb: CallbackQuery, text, kb):
    if cb.message.photo:
        await cb.message.delete()
        await cb.message.answer(text, reply_markup=kb)
    else:
        await cb.message.edit_text(text, reply_markup=kb)

@r.message(CommandStart())
async def start(m: Message, state: FSMContext):
    await state.clear()
    is_admin = (m.from_user.id == BOSS)
    await m.answer(HOME_TEXT, reply_markup=home_kb(is_admin))

@r.callback_query(F.data == "home")
async def home(cb: CallbackQuery):
    is_admin = (cb.from_user.id == BOSS)
    await show(cb, HOME_TEXT, home_kb(is_admin))

# --- ADMIN PANEL ---
@r.message(Command("admin"))
@r.callback_query(F.data == "admin_panel")
async def admin_panel(event):
    uid = event.from_user.id
    if uid != BOSS:
        if isinstance(event, CallbackQuery):
            await event.answer("Siz admin emassiz!", show_alert=True)
        return
    
    text = (
        "⚙️ <b>Admin Panel</b>\n\n"
        "Tovarlarga rasm qo'shish uchun:\n"
        "1. Menga rasm (foto) yuboring.\n"
        "2. Rasm tagiga (caption) o'sha tovarning <b>ID raqamini</b> yozing (masalan: <code>1</code>)."
    )
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="🏠 Bosh sahifa", callback_data="home"))
    
    if isinstance(event, CallbackQuery):
        await show(event, text, kb.as_markup())
    else:
        await event.answer(text, reply_markup=kb.as_markup(), parse_mode="HTML")

@r.message(F.photo, F.from_user.id == BOSS)
async def save_product_photo(m: Message):
    caption = m.caption
    if not caption or not caption.strip().isdigit():
        await m.reply("❌ Xato! Rasm tagiga tovarning raqamli ID sini yozib yuboring (masalan: 1).")
        return
    
    pid = int(caption.strip())
    photo_id = m.photo[-1].file_id
    
    product = db.execute("select * from products where id=?", (pid,)).fetchone()
    if not product:
        await m.reply(f"❌ #{pid} raqamli tovar topilmadi!")
        return
    
    db.execute("update products set photo=? where id=?", (photo_id, pid))
    db.commit()
    await m.reply(f"✅ #{pid} ({product['name']}) uchun rasm muvaffaqiyatli saqlandi!")

# --- KATALOG VA MAHSULOTLAR ---
@r.callback_query(F.data.startswith("c:"))
async def cat_page(cb: CallbackQuery):
    _, i, p = cb.data.split(":")
    i, p = int(i), int(p)
    category_list = cats()
    if i >= len(category_list):
        await cb.answer("Bo'lim topilmadi", show_alert=True)
        return
    cat = category_list[i]
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
    
    caption = f"<b>🆔 ID: {x['id']} | {html.escape(x['name'])}</b>\n💰 {money(x['price'])}"
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
        await show(cb, "🛒 Savat bo'sh.", home_kb(uid == BOSS))
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
    await cb.message.edit_text("🗑 Savat tozalandi.", reply_markup=home_kb(cb.from_user.id == BOSS))

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
    await cb.message.edit_text("Bekor qilindi.", reply_markup=home_kb(cb.from_user.id == BOSS))

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
        f"{html.escape(body)}\n\n💰 Jami: <b>{money(total)}</b>\n"
        f"📞 Boshliq raqami: {BOSS_PHONE}")
    await state.clear()
    await cb.message.edit_text(f"✅ Buyurtma #{oid} qabul qilindi! Tez orada bog'lanamiz.")

@r.message(StateFilter(None), F.text, ~F.text.startswith("/"))
async def search(m: Message):
    rows = db.execute("select * from products where name like ? limit 15", (f"%{m.text}%",)).fetchall()
    if not rows:
        await m.answer("Topilmadi. Boshqa nom yozing.", reply_markup=home_kb(m.from_user.id == BOSS))
        return
    kb = InlineKeyboardBuilder()
    for x in rows:
        kb.button(text=f"ID:{x['id']} | {x['name']} — {money(
