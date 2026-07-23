import logging
import os
from html import escape

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ["BOT_TOKEN"].strip()
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "8279849914"))
PAYMENT_GROUP_ID = int(os.getenv("PAYMENT_GROUP_ID", str(ADMIN_CHAT_ID)))
SUPPORT_GROUP_ID = int(os.getenv("SUPPORT_GROUP_ID", str(ADMIN_CHAT_ID)))
COMPANY_NAME = os.getenv("COMPANY_NAME", "HD Sportwear")
SITE_URL = os.getenv("SITE_URL", "https://hdsportwear.shop")
CATALOG_URL = os.getenv("CATALOG_URL", SITE_URL)
DELIVERY_URL = os.getenv("DELIVERY_URL", f"{SITE_URL}/delivery")
MANAGER_URL = os.getenv("MANAGER_URL", "https://t.me/Danil_HDsportwear")
PAYMENT_RECIPIENT = "Харланова Наталія Олексіївна"
PAYMENT_IBAN = "UA173006140000026004500659353"
PAYMENT_BANK = "АТ «КРЕДІ АГРІКОЛЬ БАНК»"
PAYMENT_TAX_ID = "1824301129"
DISCOUNT_UAH = int(os.getenv("DISCOUNT_UAH", "100"))

(
    NAME,
    PHONE,
    ORDER_NUMBER,
    PRODUCT,
    SIZE,
    AMOUNT,
    RECEIPT,
    SUPPORT_PHONE,
    SUPPORT_ORDER,
    SUPPORT_MESSAGE,
    EXCHANGE_ORDER,
    EXCHANGE_PHONE,
    EXCHANGE_DESCRIPTION,
    EXCHANGE_MEDIA,
) = range(14)


def main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [
            ["🛍 Каталог", "📏 Підібрати розмір"],
            ["💳 Оплата", "🚚 Доставка"],
            ["🔄 Обмін та повернення"],
            ["💬 Поставити питання", "👨‍💼 Менеджер"],
        ],
        resize_keyboard=True,
    )


def payment_intro_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("➡️ Продовжити", callback_data="payment_start")],
            [InlineKeyboardButton("👨‍💼 Поставити питання менеджеру", callback_data="support_start")],
        ]
    )


def trust_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🌐 Офіційний сайт", url=SITE_URL)],
            [InlineKeyboardButton("💳 Перейти до оплати", callback_data="payment_start")],
            [InlineKeyboardButton("👨‍💼 Менеджер", callback_data="support_start")],
        ]
    )


def help_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("📏 Допомогти з розміром", callback_data="faq:size")],
            [InlineKeyboardButton("🧵 Питання про тканину", callback_data="faq:fabric")],
            [InlineKeyboardButton("💳 Питання про оплату", callback_data="faq:payment")],
            [InlineKeyboardButton("🚚 Питання про доставку", callback_data="faq:delivery")],
            [InlineKeyboardButton("🔄 Обмін та повернення", callback_data="exchange_menu")],
            [InlineKeyboardButton("📦 Статус замовлення", callback_data="support_status")],
            [InlineKeyboardButton("✍️ Поставити своє питання", callback_data="support_start")],
        ]
    )


def exchange_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("📏 Не підійшов розмір", callback_data="exchange:size")],
            [InlineKeyboardButton("🎨 Інший колір або модель", callback_data="exchange:color")],
            [InlineKeyboardButton("↩️ Повернення товару", callback_data="exchange:return")],
            [InlineKeyboardButton("⚠️ Виявлено дефект", callback_data="exchange:defect")],
            [InlineKeyboardButton("❓ Інша ситуація", callback_data="exchange:other")],
            [InlineKeyboardButton("📋 Умови обміну", callback_data="faq:exchange_rules")],
        ]
    )


def manager_review_keyboard(user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("✅ Оплату підтверджено", callback_data=f"payment_ok:{user_id}")],
            [InlineKeyboardButton("❌ Оплату не знайдено", callback_data=f"payment_missing:{user_id}")],
        ]
    )


def support_review_keyboard(user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("✅ Взяти в роботу", callback_data=f"support_taken:{user_id}")]]
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    payload = context.args[0] if context.args else None
    if payload:
        context.user_data["deep_link_order"] = payload
    await update.message.reply_text(
        f"👋 <b>Вітаємо в офіційному боті {escape(COMPANY_NAME)}!</b>\n\n"
        "Я допоможу переглянути каталог, підібрати розмір, дізнатися умови доставки, "
        "отримати реквізити для оплати або оформити звернення щодо обміну та повернення.\n\n"
        f"🎁 При повній оплаті на рахунок ФОП діє <b>знижка {DISCOUNT_UAH} грн</b>.",
        parse_mode=ParseMode.HTML,
        reply_markup=main_menu(),
    )


async def chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        f"ID цього чату: <code>{update.effective_chat.id}</code>",
        parse_mode=ParseMode.HTML,
    )


async def catalog(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "🛍 <b>Каталог HD Sportwear</b>\n\n"
        "Перегляньте актуальні моделі, кольори та ціни на нашому офіційному сайті.",
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("🛍 Відкрити каталог", url=CATALOG_URL)],
                [InlineKeyboardButton("📏 Допомогти з розміром", callback_data="support_size")],
            ]
        ),
    )


async def size_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "📏 <b>Підбір розміру</b>\n\n"
        "Щоб менеджер точно підібрав розмір, підготуйте:\n"
        "• фото або назву моделі;\n"
        "• обхват грудей;\n"
        "• обхват талії;\n"
        "• обхват стегон;\n"
        "• зріст.\n\n"
        "Натисніть кнопку нижче — бот збере контактні дані та передасть звернення менеджеру.",
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("📏 Підібрати розмір", callback_data="support_size")]]
        ),
    )


async def payment_offer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (
        f"🎁 <b>Знижка {DISCOUNT_UAH} грн при повній оплаті</b>\n\n"
        "Оплатіть замовлення на офіційний рахунок ФОП та отримайте:\n\n"
        f"✅ мінус {DISCOUNT_UAH} грн від вартості товару\n"
        "✅ без комісії за післяплату Нової пошти\n"
        "✅ швидшу обробку замовлення\n\n"
        "Перед реквізитами бот збере мінімальну інформацію, щоб менеджер точно прив’язав оплату до вашого замовлення."
    )
    await update.message.reply_text(text, parse_mode=ParseMode.HTML, reply_markup=payment_intro_keyboard())


async def trust(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (
        "🛡️ <b>Безпечна оплата</b>\n\n"
        f"Ви оплачуєте замовлення безпосередньо на <b>офіційний рахунок ФОП виробника {escape(COMPANY_NAME)}</b>, "
        "а не на особисту банківську картку.\n\n"
        "✅ понад 10 років роботи\n"
        "✅ власне виробництво у Харкові\n"
        "✅ офіційний рахунок ФОП\n"
        "✅ відправлення по всій Україні\n"
        "✅ квитанцію перевіряє живий менеджер\n\n"
        "Після підтвердження платежу замовлення передається на комплектацію або у виробництво."
    )
    await update.message.reply_text(text, parse_mode=ParseMode.HTML, reply_markup=trust_keyboard())


async def delivery(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "📦 <b>Доставка та оплата</b>\n\n"
        "🚚 Відправляємо Новою поштою по всій Україні.\n"
        "💳 Повна оплата здійснюється на офіційний рахунок ФОП.\n"
        f"🎁 При повній оплаті діє знижка {DISCOUNT_UAH} грн.\n"
        "✅ Після оплати квитанцію можна надіслати прямо в цей бот.\n\n"
        "Докладні умови можна переглянути на сайті.",
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("📋 Умови доставки та оплати", url=DELIVERY_URL)],
                [InlineKeyboardButton("🎁 Отримати знижку", callback_data="payment_start")],
                [InlineKeyboardButton("❓ Поставити питання", callback_data="support_start")],
            ]
        ),
    )


async def help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "❓ <b>Допомога клієнтам</b>\n\nОберіть тему або залиште своє питання. Менеджер отримає звернення прямо в робочу групу.",
        parse_mode=ParseMode.HTML,
        reply_markup=help_keyboard(),
    )


async def exchange_menu_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "🔄 <b>Обмін та повернення</b>\n\nОберіть причину звернення. Бот збере необхідні дані та передасть їх менеджеру.",
        parse_mode=ParseMode.HTML,
        reply_markup=exchange_keyboard(),
    )


async def exchange_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    await query.message.reply_text(
        "🔄 <b>Обмін та повернення</b>\n\nОберіть причину звернення.",
        parse_mode=ParseMode.HTML,
        reply_markup=exchange_keyboard(),
    )


async def manager(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Менеджер допоможе з оформленням, розміром, оплатою, доставкою, обміном або поверненням.",
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("✍️ Залишити звернення", callback_data="support_start")],
                [InlineKeyboardButton("Відкрити чат менеджера", url=MANAGER_URL)],
            ]
        ),
    )


async def faq_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    topic = query.data.split(":", 1)[1]
    answers = {
        "size": (
            "📏 <b>Допомога з розміром</b>\n\n"
            "Для точного підбору надішліть менеджеру:\n"
            "• назву або фото моделі;\n• обхват грудей;\n• обхват талії;\n• обхват стегон;\n• зріст.\n\n"
            "Не обирайте розмір лише за звичним номером — посадка залежить від моделі та тканини."
        ),
        "fabric": (
            "🧵 <b>Питання про тканину</b>\n\n"
            "Напишіть назву моделі або надішліть її фото менеджеру. Ми уточнимо склад, щільність, сезонність, "
            "еластичність тканини та рекомендації з догляду."
        ),
        "payment": (
            f"💳 <b>Оплата</b>\n\nПовна оплата здійснюється на офіційний рахунок ФОП. "
            f"При повній оплаті діє знижка <b>{DISCOUNT_UAH} грн</b>. Після платежу квитанцію потрібно надіслати в бот."
        ),
        "delivery": (
            "🚚 <b>Доставка</b>\n\nВідправляємо замовлення Новою поштою по всій Україні. "
            "Термін підготовки залежить від наявності товару або необхідності виготовлення."
        ),
        "exchange_rules": (
            "📋 <b>Основні умови обміну та повернення</b>\n\n"
            "✅ товар не був у використанні;\n"
            "✅ збережено товарний вигляд, бірки та упаковку;\n"
            "✅ немає слідів косметики, парфумів, прання або інших забруднень.\n\n"
            "Будь ласка, не відправляйте посилку самостійно. Спочатку оформіть звернення, і менеджер надасть інструкцію."
        ),
    }
    await query.message.reply_text(
        answers.get(topic, "Оберіть потрібний розділ."),
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("👨‍💼 Уточнити у менеджера", callback_data="support_start")]]
        ),
    )


async def begin_payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    deep_link_order = context.user_data.get("deep_link_order")
    if deep_link_order:
        context.user_data["order_number"] = deep_link_order
    await query.message.reply_text("Як вас звати? Вкажіть ім’я та прізвище.", reply_markup=ReplyKeyboardRemove())
    return NAME


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["name"] = update.message.text.strip()
    await update.message.reply_text(
        "Вкажіть номер телефону, на який оформлено замовлення.",
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton("📱 Надіслати номер", request_contact=True)]],
            resize_keyboard=True,
            one_time_keyboard=True,
        ),
    )
    return PHONE


async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    phone = update.message.contact.phone_number if update.message.contact else update.message.text.strip()
    digits = "".join(ch for ch in phone if ch.isdigit())
    if len(digits) < 10:
        await update.message.reply_text("Перевірте номер і введіть його ще раз.")
        return PHONE
    context.user_data["phone"] = phone
    if context.user_data.get("order_number"):
        await update.message.reply_text(
            f"Номер замовлення отримано: <b>{escape(context.user_data['order_number'])}</b>\n\nЯкий товар ви замовили?",
            parse_mode=ParseMode.HTML,
            reply_markup=ReplyKeyboardRemove(),
        )
        return PRODUCT
    await update.message.reply_text("Вкажіть номер замовлення. Якщо його немає — напишіть «Далі».", reply_markup=ReplyKeyboardRemove())
    return ORDER_NUMBER


async def get_order_number(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    value = update.message.text.strip()
    context.user_data["order_number"] = "Не вказано" if value.lower() in {"далі", "пропустити"} else value
    await update.message.reply_text("Який товар ви замовили?")
    return PRODUCT


async def get_product(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["product"] = update.message.text.strip()
    await update.message.reply_text("Вкажіть розмір. Якщо не знаєте — напишіть «Далі».")
    return SIZE


async def get_size(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    value = update.message.text.strip()
    context.user_data["size"] = "Не вказано" if value.lower() in {"далі", "пропустити"} else value
    await update.message.reply_text("Вкажіть суму замовлення <b>до знижки</b> цифрами, наприклад: 699", parse_mode=ParseMode.HTML)
    return AMOUNT


async def get_amount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    raw = update.message.text.strip().replace(" ", "").replace(",", ".")
    try:
        original = float(raw)
    except ValueError:
        await update.message.reply_text("Введіть суму цифрами, наприклад: 699")
        return AMOUNT
    payable = max(0, original - DISCOUNT_UAH)
    context.user_data["original_amount"] = original
    context.user_data["payable_amount"] = payable
    await update.message.reply_text(
        "🛡️ <b>Безпечна оплата</b>\n\n"
        f"Отримувач: <b>{escape(PAYMENT_RECIPIENT)}</b>\n"
        f"Банк: <b>{escape(PAYMENT_BANK)}</b>\n"
        f"IBAN:\n<code>{escape(PAYMENT_IBAN)}</code>\n"
        f"ІПН: <code>{escape(PAYMENT_TAX_ID)}</code>\n\n"
        f"Вартість замовлення: <s>{original:.0f} грн</s>\n"
        f"Знижка: <b>−{DISCOUNT_UAH} грн</b>\n"
        f"До сплати: <b>{payable:.0f} грн</b>\n\n"
        f"Призначення платежу:\n<code>Оплата за товар</code>\n\n"
        "Після оплати надішліть сюди фото, скриншот або PDF-квитанцію.",
        parse_mode=ParseMode.HTML,
    )
    return RECEIPT


async def receive_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    data = context.user_data
    username = f"@{user.username}" if user.username else "немає"
    caption = (
        "💳 <b>НОВА ОПЛАТА</b>\n\n"
        f"👤 Клієнт: <b>{escape(data.get('name', ''))}</b>\n"
        f"📞 Телефон: <code>{escape(data.get('phone', ''))}</code>\n"
        f"🔗 Telegram: {escape(username)}\n"
        f"🧾 Замовлення: <b>{escape(data.get('order_number', ''))}</b>\n"
        f"👕 Товар: <b>{escape(data.get('product', ''))}</b>\n"
        f"📏 Розмір: <b>{escape(data.get('size', ''))}</b>\n"
        f"💰 Сума до знижки: <b>{data.get('original_amount', 0):.0f} грн</b>\n"
        f"🎁 Знижка: <b>−{DISCOUNT_UAH} грн</b>\n"
        f"✅ Очікувана оплата: <b>{data.get('payable_amount', 0):.0f} грн</b>"
    )
    markup = manager_review_keyboard(user.id)
    if update.message.photo:
        await context.bot.send_photo(chat_id=PAYMENT_GROUP_ID, photo=update.message.photo[-1].file_id, caption=caption, parse_mode=ParseMode.HTML, reply_markup=markup)
    elif update.message.document:
        await context.bot.send_document(chat_id=PAYMENT_GROUP_ID, document=update.message.document.file_id, caption=caption, parse_mode=ParseMode.HTML, reply_markup=markup)
    else:
        await update.message.reply_text("Надішліть фото, скриншот або PDF-квитанцію.")
        return RECEIPT
    await update.message.reply_text(
        "✅ <b>Квитанцію отримано!</b>\n\nДякуємо! Менеджер уже перевіряє вашу оплату.\n\n"
        "Будь ласка, не здійснюйте повторний платіж. Після перевірки ми повідомимо результат у цьому чаті.",
        parse_mode=ParseMode.HTML,
        reply_markup=main_menu(),
    )
    context.user_data.clear()
    return ConversationHandler.END


async def begin_support(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data["request_type"] = "Допомога клієнту"
    await query.message.reply_text(
        "📞 Вкажіть номер телефону, за яким менеджер зможе знайти замовлення або зв’язатися з вами.",
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton("📱 Надіслати номер", request_contact=True)]], resize_keyboard=True, one_time_keyboard=True),
    )
    return SUPPORT_PHONE


async def begin_status_support(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data["request_type"] = "Статус замовлення"
    await query.message.reply_text(
        "📞 Вкажіть номер телефону, на який оформлено замовлення.",
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton("📱 Надіслати номер", request_contact=True)]], resize_keyboard=True, one_time_keyboard=True),
    )
    return SUPPORT_PHONE


async def begin_size_support(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data["request_type"] = "Підбір розміру"
    await query.message.reply_text(
        "📞 Вкажіть номер телефону, за яким менеджер зможе зв’язатися з вами.",
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton("📱 Надіслати номер", request_contact=True)]], resize_keyboard=True, one_time_keyboard=True),
    )
    return SUPPORT_PHONE


async def support_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    phone = update.message.contact.phone_number if update.message.contact else update.message.text.strip()
    if len("".join(ch for ch in phone if ch.isdigit())) < 10:
        await update.message.reply_text("Перевірте номер телефону і введіть його ще раз.")
        return SUPPORT_PHONE
    context.user_data["support_phone"] = phone
    await update.message.reply_text("Вкажіть номер замовлення. Якщо його немає — напишіть «Далі».", reply_markup=ReplyKeyboardRemove())
    return SUPPORT_ORDER


async def support_order(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    value = update.message.text.strip()
    context.user_data["support_order"] = "Не вказано" if value.lower() in {"далі", "пропустити"} else value
    await update.message.reply_text("Опишіть ваше питання одним повідомленням. Додайте назву товару, розмір або інші важливі подробиці.")
    return SUPPORT_MESSAGE


async def support_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    username = f"@{user.username}" if user.username else "немає"
    text = (
        "❓ <b>НОВЕ ЗВЕРНЕННЯ КЛІЄНТА</b>\n\n"
        f"📌 Тип: <b>{escape(context.user_data.get('request_type', 'Допомога клієнту'))}</b>\n"
        f"👤 Клієнт: <b>{escape(user.full_name)}</b>\n"
        f"🔗 Telegram: {escape(username)}\n"
        f"📞 Телефон: <code>{escape(context.user_data.get('support_phone', ''))}</code>\n"
        f"🧾 Замовлення: <b>{escape(context.user_data.get('support_order', 'Не вказано'))}</b>\n\n"
        f"💬 Повідомлення:\n{escape(update.message.text.strip())}"
    )
    await context.bot.send_message(chat_id=SUPPORT_GROUP_ID, text=text, parse_mode=ParseMode.HTML, reply_markup=support_review_keyboard(user.id))
    await update.message.reply_text(
        "✅ <b>Звернення прийнято!</b>\n\nМенеджер отримав ваше питання і зв’яжеться з вами після перевірки інформації.",
        parse_mode=ParseMode.HTML,
        reply_markup=main_menu(),
    )
    context.user_data.clear()
    return ConversationHandler.END


async def begin_exchange(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    reason_code = query.data.split(":", 1)[1]
    reasons = {
        "size": "Не підійшов розмір",
        "color": "Потрібен інший колір або модель",
        "return": "Повернення товару",
        "defect": "Виявлено дефект",
        "other": "Інша ситуація",
    }
    context.user_data["exchange_reason"] = reasons.get(reason_code, "Інша ситуація")
    await query.message.reply_text("Вкажіть номер замовлення. Якщо його немає — напишіть «Далі».", reply_markup=ReplyKeyboardRemove())
    return EXCHANGE_ORDER


async def exchange_order(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    value = update.message.text.strip()
    context.user_data["exchange_order"] = "Не вказано" if value.lower() in {"далі", "пропустити"} else value
    await update.message.reply_text(
        "Вкажіть номер телефону, на який оформлено замовлення.",
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton("📱 Надіслати номер", request_contact=True)]], resize_keyboard=True, one_time_keyboard=True),
    )
    return EXCHANGE_PHONE


async def exchange_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    phone = update.message.contact.phone_number if update.message.contact else update.message.text.strip()
    if len("".join(ch for ch in phone if ch.isdigit())) < 10:
        await update.message.reply_text("Перевірте номер телефону і введіть його ще раз.")
        return EXCHANGE_PHONE
    context.user_data["exchange_phone"] = phone
    await update.message.reply_text(
        "Опишіть ситуацію: який товар отримали, який розмір, що саме потрібно обміняти або повернути.",
        reply_markup=ReplyKeyboardRemove(),
    )
    return EXCHANGE_DESCRIPTION


async def exchange_description(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["exchange_description"] = update.message.text.strip()
    await update.message.reply_text(
        "Надішліть фото товару або дефекту. Якщо фото не потрібне — натисніть «Далі».",
        reply_markup=ReplyKeyboardMarkup([["Далі"]], resize_keyboard=True, one_time_keyboard=True),
    )
    return EXCHANGE_MEDIA


async def finish_exchange(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    username = f"@{user.username}" if user.username else "немає"
    caption = (
        "🔄 <b>НОВЕ ЗВЕРНЕННЯ: ОБМІН / ПОВЕРНЕННЯ</b>\n\n"
        f"📌 Причина: <b>{escape(context.user_data.get('exchange_reason', ''))}</b>\n"
        f"👤 Клієнт: <b>{escape(user.full_name)}</b>\n"
        f"🔗 Telegram: {escape(username)}\n"
        f"📞 Телефон: <code>{escape(context.user_data.get('exchange_phone', ''))}</code>\n"
        f"🧾 Замовлення: <b>{escape(context.user_data.get('exchange_order', ''))}</b>\n\n"
        f"💬 Опис:\n{escape(context.user_data.get('exchange_description', ''))}"
    )
    markup = support_review_keyboard(user.id)
    if update.message.photo:
        await context.bot.send_photo(chat_id=SUPPORT_GROUP_ID, photo=update.message.photo[-1].file_id, caption=caption, parse_mode=ParseMode.HTML, reply_markup=markup)
    elif update.message.document:
        await context.bot.send_document(chat_id=SUPPORT_GROUP_ID, document=update.message.document.file_id, caption=caption, parse_mode=ParseMode.HTML, reply_markup=markup)
    else:
        await context.bot.send_message(chat_id=SUPPORT_GROUP_ID, text=caption, parse_mode=ParseMode.HTML, reply_markup=markup)
    await update.message.reply_text(
        "✅ <b>Звернення прийнято!</b>\n\n"
        "Ми передали інформацію менеджеру. Не видаляйте бірки та не відправляйте товар, доки менеджер не надасть інструкцію.",
        parse_mode=ParseMode.HTML,
        reply_markup=main_menu(),
    )
    context.user_data.clear()
    return ConversationHandler.END


async def manager_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    action, raw_user_id = query.data.split(":", 1)
    target_user_id = int(raw_user_id)
    allowed_groups = {PAYMENT_GROUP_ID, SUPPORT_GROUP_ID}
    if query.from_user.id != ADMIN_CHAT_ID and query.message.chat_id not in allowed_groups:
        await query.answer("Недостатньо прав", show_alert=True)
        return
    if action == "payment_ok":
        await context.bot.send_message(
            chat_id=target_user_id,
            text=(
                "✅ <b>Оплату підтверджено!</b>\n\n"
                f"Дякуємо за замовлення в {escape(COMPANY_NAME)} ❤️\n"
                "Замовлення передано на комплектацію або у виробництво. Після відправлення менеджер повідомить номер ТТН."
            ),
            parse_mode=ParseMode.HTML,
        )
        status_text = f"✅ Підтвердив(ла): {escape(query.from_user.full_name)}"
    elif action == "payment_missing":
        await context.bot.send_message(
            chat_id=target_user_id,
            text="⚠️ <b>Оплату поки не знайдено</b>\n\nНе здійснюйте повторний платіж. Менеджер зв’яжеться з вами для уточнення.",
            parse_mode=ParseMode.HTML,
        )
        status_text = f"⚠️ Позначив(ла): {escape(query.from_user.full_name)}"
    else:
        await context.bot.send_message(
            chat_id=target_user_id,
            text=(
                "👨‍💼 <b>Менеджер узяв ваше звернення в роботу</b>\n\n"
                "Ми перевіряємо інформацію та зв’яжемося з вами для вирішення питання."
            ),
            parse_mode=ParseMode.HTML,
        )
        status_text = f"✅ Взяв(ла) в роботу: {escape(query.from_user.full_name)}"
    await query.edit_message_reply_markup(reply_markup=None)
    await query.message.reply_text(status_text, parse_mode=ParseMode.HTML)


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    await update.message.reply_text("Операцію скасовано.", reply_markup=main_menu())
    return ConversationHandler.END


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.exception("Unhandled error", exc_info=context.error)


def build_application() -> Application:
    application = Application.builder().token(BOT_TOKEN).build()

    payment_conversation = ConversationHandler(
        entry_points=[CallbackQueryHandler(begin_payment, pattern="^payment_start$")],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            PHONE: [MessageHandler(filters.CONTACT, get_phone), MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            ORDER_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_order_number)],
            PRODUCT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_product)],
            SIZE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_size)],
            AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_amount)],
            RECEIPT: [MessageHandler(filters.PHOTO | filters.Document.ALL, receive_receipt)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
    )

    support_conversation = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(begin_support, pattern="^support_start$"),
            CallbackQueryHandler(begin_status_support, pattern="^support_status$"),
            CallbackQueryHandler(begin_size_support, pattern="^support_size$"),
        ],
        states={
            SUPPORT_PHONE: [MessageHandler(filters.CONTACT, support_phone), MessageHandler(filters.TEXT & ~filters.COMMAND, support_phone)],
            SUPPORT_ORDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, support_order)],
            SUPPORT_MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, support_message)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
    )

    exchange_conversation = ConversationHandler(
        entry_points=[CallbackQueryHandler(begin_exchange, pattern=r"^exchange:(size|color|return|defect|other)$")],
        states={
            EXCHANGE_ORDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, exchange_order)],
            EXCHANGE_PHONE: [MessageHandler(filters.CONTACT, exchange_phone), MessageHandler(filters.TEXT & ~filters.COMMAND, exchange_phone)],
            EXCHANGE_DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, exchange_description)],
            EXCHANGE_MEDIA: [MessageHandler(filters.PHOTO | filters.Document.ALL | (filters.TEXT & ~filters.COMMAND), finish_exchange)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("chatid", chat_id))
    application.add_handler(payment_conversation)
    application.add_handler(support_conversation)
    application.add_handler(exchange_conversation)
    application.add_handler(CallbackQueryHandler(faq_callback, pattern=r"^faq:"))
    application.add_handler(CallbackQueryHandler(exchange_menu_callback, pattern="^exchange_menu$"))
    application.add_handler(CallbackQueryHandler(manager_callback, pattern=r"^(payment_ok|payment_missing|support_taken):\d+$"))
    application.add_handler(MessageHandler(filters.Regex("^🛍 Каталог$"), catalog))
    application.add_handler(MessageHandler(filters.Regex("^📏 Підібрати розмір$"), size_help))
    application.add_handler(MessageHandler(filters.Regex("^💳 Оплата$"), payment_offer))
    application.add_handler(MessageHandler(filters.Regex("^🚚 Доставка$"), delivery))
    application.add_handler(MessageHandler(filters.Regex("^🔄 Обмін та повернення$"), exchange_menu_message))
    application.add_handler(MessageHandler(filters.Regex("^💬 Поставити питання$"), help_menu))
    application.add_handler(MessageHandler(filters.Regex("^👨‍💼 Менеджер$"), manager))
    # Старі назви кнопок залишені для сумісності зі старими повідомленнями.
    application.add_handler(MessageHandler(filters.Regex("^🎁 Отримати знижку 100 грн$"), payment_offer))
    application.add_handler(MessageHandler(filters.Regex("^🛡️ Чому нам довіряють$"), trust))
    application.add_handler(MessageHandler(filters.Regex("^📦 Доставка та оплата$"), delivery))
    application.add_handler(MessageHandler(filters.Regex("^❓ Допомога$"), help_menu))
    application.add_error_handler(error_handler)
    return application


if __name__ == "__main__":
    app = build_application()
    logger.info("Starting HD Sportwear bot")
    app.run_polling(allowed_updates=Update.ALL_TYPES)
