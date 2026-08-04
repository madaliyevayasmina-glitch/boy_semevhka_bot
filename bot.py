import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage


# =========================
# BOT TOKEN
# =========================

TOKEN = "8996960424:AAEv1r_9bqfiqhAp2szwnZnYx0KgPle7MDM"


# =========================
# ADMIN TELEGRAM ID
# =========================

ADMIN_ID = 171284166


# =========================
# MAHSULOTLAR
# =========================

PRODUCTS = {
    "boy_3kg": ("🌻 Semechka Boy 3kg", 108000),
    "boy_shor_3kg": ("🧂 Semechka Boy sho'r 3kg", 106500),

    "boy_5kg": ("🌻 Semechka Boy 5kg", 180000),
    "boy_shor_5kg": ("🧂 Semechka Boy sho'r 5kg", 177500),

    "boy_10kg": ("🌻 Semechka Boy 10kg", 350000),
    "boy_shor_10kg": ("🧂 Semechka Boy sho'r 10kg", 345000),

    "boy_25kg": ("🌻 Semechka Boy 25kg", 862500),
    "boy_shor_25kg": ("🧂 Semechka Boy sho'r 25kg", 850000),

    "yeryongoq_1kg": ("🥜 Yeryong'oq 1kg", 23000),
    "qurut_1kg": ("🧀 Toza Qurut 1kg", 80000),
    "chips_chicco": ("🍟 Chips Chicco", 52000),
}


# =========================
# BOTNI ISHGA TUSHIRISH
# =========================

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())


# =========================
# BUYURTMA HOLATLARI
# =========================

class OrderState(StatesGroup):
    phone = State()
    address = State()


# =========================
# ASOSIY MENYU
# =========================

def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🛍 Mahsulotlar"),
                KeyboardButton(text="🛒 Savatim"),
            ],
            [
                KeyboardButton(text="📞 Aloqa"),
            ],
        ],
        resize_keyboard=True
    )


# =========================
# MAHSULOTLAR MENYUSI
# =========================

def products_menu():
    buttons = []

    for product_id, (name, price) in PRODUCTS.items():
        buttons.append([
            InlineKeyboardButton(
                text=f"{name} — {price:,} so'm".replace(",", " "),
                callback_data=f"product:{product_id}"
            )
        ])

    buttons.append([
        InlineKeyboardButton(
            text="◀️ Orqaga",
            callback_data="back_menu"
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


# =========================
# MAHSULOT TUGMALARI
# =========================

def product_buttons(product_id):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🛒 Savatga qo'shish",
                    callback_data=f"add:{product_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="◀️ Mahsulotlarga qaytish",
                    callback_data="products"
                )
            ]
        ]
    )


# =========================
# START
# =========================

@dp.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):

    await state.clear()

    await message.answer(
        f"👋 Assalomu alaykum, {message.from_user.first_name}!\n\n"
        "🌻 **BOY SEMECHKА** botiga xush kelibsiz!\n\n"
        "🛍 Kerakli bo'limni tanlang:",
        reply_markup=main_menu(),
        parse_mode="Markdown"
    )


# =========================
# MAHSULOTLAR
# =========================

@dp.message(F.text == "🛍 Mahsulotlar")
async def products_handler(message: Message):

    await message.answer(
        "🛍 **Mahsulotlarimiz:**\n\n"
        "Kerakli mahsulotni tanlang:",
        reply_markup=products_menu(),
        parse_mode="Markdown"
    )


# =========================
# MAHSULOTNI KO'RISH
# =========================

@dp.callback_query(F.data.startswith("product:"))
async def product_handler(callback: CallbackQuery):

    product_id = callback.data.split(":")[1]

    name, price = PRODUCTS[product_id]

    await callback.message.edit_text(
        f"{name}\n\n"
        f"💰 Narxi: **{price:,} so'm**\n\n"
        "🛒 Mahsulotni savatga qo'shish uchun tugmani bosing.",
        reply_markup=product_buttons(product_id),
        parse_mode="Markdown"
    )

    await callback.answer()


# =========================
# SAVATGA QO'SHISH
# =========================

@dp.callback_query(F.data.startswith("add:"))
async def add_to_cart(callback: CallbackQuery, state: FSMContext):

    product_id = callback.data.split(":")[1]

    data = await state.get_data()

    cart = data.get("cart", {})

    cart[product_id] = cart.get(product_id, 0) + 1

    await state.update_data(cart=cart)

    name, price = PRODUCTS[product_id]

    await callback.answer(
        f"✅ {name} savatga qo'shildi!",
        show_alert=True
    )

    await callback.message.answer(
        f"✅ **{name}** savatga qo'shildi!\n\n"
        "🛍 Yana mahsulot tanlashingiz yoki 🛒 savatni ko'rishingiz mumkin.",
        parse_mode="Markdown"
    )


# =========================
# SAVATNI KO'RISH
# =========================

@dp.message(F.text == "🛒 Savatim")
async def cart_handler(message: Message, state: FSMContext):

    data = await state.get_data()

    cart = data.get("cart", {})

    if not cart:

        await message.answer(
            "🛒 Savatingiz hozircha bo'sh.\n\n"
            "Mahsulotlar bo'limidan mahsulot tanlang.",
            reply_markup=main_menu()
        )

        return

    text = "🛒 **Sizning savatingiz:**\n\n"

    total = 0

    for product_id, quantity in cart.items():

        name, price = PRODUCTS[product_id]

        summa = price * quantity

        total += summa

        text += (
            f"📦 {name}\n"
            f"🔢 Miqdori: {quantity} dona\n"
            f"💰 Summa: {summa:,} so'm\n\n"
        )

    text += (
        "━━━━━━━━━━━━━━\n"
        f"💵 **Jami: {total:,} so'm**"
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📦 Buyurtma berish",
                    callback_data="order"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🗑 Savatni tozalash",
                    callback_data="clear_cart"
                )
            ]
        ]
    )

    await message.answer(
        text,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )


# =========================
# SAVATNI TOZALASH
# =========================

@dp.callback_query(F.data == "clear_cart")
async def clear_cart(callback: CallbackQuery, state: FSMContext):

    await state.update_data(cart={})

    await callback.message.edit_text(
        "🗑 Savat tozalandi.\n\n"
        "Endi savatingiz bo'sh."
    )

    await callback.answer("Savat tozalandi")


# =========================
# BUYURTMA BERISH
# =========================

@dp.callback_query(F.data == "order")
async def order_handler(callback: CallbackQuery, state: FSMContext):

    data = await state.get_data()

    cart = data.get("cart", {})

    if not cart:

        await callback.answer(
            "Savat bo'sh!",
            show_alert=True
        )

        return

    await callback.message.answer(
        "📞 Buyurtmani rasmiylashtirish uchun telefon raqamingizni yuboring.\n\n"
        "Masalan: +998 90 123 45 67"
    )

    await state.set_state(OrderState.phone)

    await callback.answer()


# =========================
# TELEFON RAQAMI
# =========================

@dp.message(OrderState.phone)
async def phone_handler(message: Message, state: FSMContext):

    phone = message.text

    await state.update_data(phone=phone)

    await message.answer(
        "📍 Endi yetkazib berish manzilingizni yozing.\n\n"
        "Masalan: Namangan shahar, Chorsu ko'chasi"
    )

    await state.set_state(OrderState.address)


# =========================
# MANZIL
# =========================

@dp.message(OrderState.address)
async def address_handler(message: Message, state: FSMContext):

    address = message.text

    data = await state.get_data()

    cart = data.get("cart", {})

    phone = data.get("phone", "Ko'rsatilmagan")

    total = 0

    order_text = "🛍 **YANGI BUYURTMA!**\n\n"

    order_text += (
        f"👤 Mijoz: {message.from_user.full_name}\n"
        f"🆔 Telegram ID: {message.from_user.id}\n"
        f"📞 Telefon: {phone}\n"
        f"📍 Manzil: {address}\n\n"
        "📦 **Mahsulotlar:**\n\n"
    )

    for product_id, quantity in cart.items():

        name, price = PRODUCTS[product_id]

        summa = price * quantity

        total += summa

        order_text += (
            f"• {name}\n"
            f"  🔢 {quantity} dona\n"
            f"  💰 {summa:,} so'm\n\n"
        )

    order_text += (
        "━━━━━━━━━━━━━━\n"
        f"💵 **JAMI: {total:,} so'm**"
    )

    # ADMINGA YUBORISH

    try:

        await bot.send_message(
            ADMIN_ID,
            order_text,
            parse_mode="Markdown"
        )

    except Exception as e:

        logging.error(f"Admin xatosi: {e}")


    # MIJOZGA JAVOB

    await message.answer(
        "✅ **Buyurtmangiz qabul qilindi!**\n\n"
        f"💵 Jami summa: **{total:,} so'm**\n\n"
        "📞 Tez orada operatorimiz siz bilan bog'lanadi.\n"
        "Rahmat! 🌻",
        reply_markup=main_menu(),
        parse_mode="Markdown"
    )

    # SAVATNI TOZALASH

    await state.clear()


# =========================
# ALOQA
# =========================

@dp.message(F.text == "📞 Aloqa")
async def contact_handler(message: Message):

    await message.answer(
        "📞 **Biz bilan bog'lanish:**\n\n"
        "Telefon: +998 93 700 48 00\n"
        "Instagram: @boy_semichka\n\n"
        "Savollaringiz bo'lsa, biz bilan bog'laning.",
        parse_mode="Markdown"
    )


# =========================
# ORQAGA
# =========================

@dp.callback_query(F.data == "back_menu")
async def back_menu_handler(callback: CallbackQuery):

    await callback.message.delete()

    await callback.message.answer(
        "🛍 Kerakli bo'limni tanlang:",
        reply_markup=main_menu()
    )

    await callback.answer()


# =========================
# MAHSULOTLARGA QAYTISH
# =========================

@dp.callback_query(F.data == "products")
async def back_products_handler(callback: CallbackQuery):

    await callback.message.edit_text(
        "🛍 **Mahsulotlarimiz:**\n\n"
        "Kerakli mahsulotni tanlang:",
        reply_markup=products_menu(),
        parse_mode="Markdown"
    )

    await callback.answer()


# =========================
# BOTNI ISHGA TUSHIRISH
# =========================

async def main():

    logging.basicConfig(level=logging.INFO)

    print("🤖 BOY SEMECHKА BOT ISHGA TUSHDI!")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())