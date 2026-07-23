import logging
import os
from html import escape

from payment_details import (
    PAYMENT_IBAN,
    PAYMENT_RECIPIENT,
    PAYMENT_TAX_ID,
)

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
COMPANY_NAME = os.getenv("COMPANY_NAME", "HD Sportwear")
SITE_URL = os.getenv("SITE_URL", "https://hdsportwear.shop")
MANAGER_URL = os.getenv("MANAGER_URL", "https://t.me/Danil_HDsportwear")
# PAYMENT_* values are loaded from payment_details.py

PAYMENT_BANK = os.getenv("PAYMENT_BANK", "АТ «КРЕДІ АГРІКОЛЬ БАНК»")

DISCOUNT_UAH = int(os.getenv("DISCOUNT_UAH", "100"))

NAME, PHONE, ORDER_NUMBER, PRODUCT, SIZE, AMOUNT, RECEIPT = range(7)


def main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [
            ["🎁 Отримати знижку 100 грн"],
            ["🛡️ Чому нам довіряють"],
            ["📦 Доставка та оплата"],
            ["👨‍💼 Менеджер"],
        ],
        resize_keyboard=True,
    )


def payment_intro_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("➡️ Продовжити", callback_data="payment_start")],
            [InlineKeyboardButton("👨‍💼 Поставити питання менеджеру", url=MANAGER_URL)],
        ]
    )


def trust_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🌐 Офіційний сайт", url=SITE_URL)],
            [InlineKeyboardButton("💳 Перейти до оплати", callback_data="payment_start")],
            [InlineKeyboardButton("👨‍💼 Менеджер", url=MANAGER_URL)],
        ]
    )


def manager_review_keyboard(user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("✅ Оплату підтверджено", callback_data=f"payment_ok:{user_id}")],
            [InlineKeyboardButton("❌ Оплату не знайдено", callback_data=f"payment_missing:{user_id}")],
        ]
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    payload = context.args[0] if context.args else None
    if payload:
        context.user_data["deep_link_order"] = payload
    await update.message.reply_text(
        f"👋 <b>Вітаємо в офіційному боті {escape(COMPANY_NAME)}!</b>\n\n"
        f"🎁 При повній оплаті на офіційний рахунок ФОП діє <b>знижка {DISCOUNT_UAH} грн</b>.\n\n"
        "Тут можна отримати реквізити, надіслати квитанцію та дочекатися підтвердження менеджера.",
        parse_mode=ParseMode.HTML,
        reply_markup=main_menu(),
    )


async def chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        f"ID цього чату: <code>{update.effective_chat.id}</code>",
        parse_mode=ParseMode.HTML,
    )


async def payment_offer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (
        f"🎁 <b>Знижка {DISCOUNT_UAH} грн при повній оплаті</b>\n\n"
        f"Оплатіть замовлення на офіційний рахунок ФОП та отримайте:\n\n"
        f"✅ мінус {DISCOUNT_UAH} грн від вартості товару\n"
        "✅ без комісії за післяплату Нової пошти\n"
        "✅ швидшу обробку замовлення\n\n"
        "Перед реквізитами бот збере мінімальну інформацію, щоб менеджер точно прив’язав оплату до вашого замовлення."
    )
    await update.message.reply_text(text, parse_mode=ParseMode.HTML, reply_markup=payment_intro_keyboard())


async def trust(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (
        "🛡️ <b>Безпечна оплата</b>\n\n"
        f"Ви оплачуєте замовлення безпосередньо на <b>офіційний рахунок ФОП виробника {escape(COMPANY_NAME)}</b>, а не на особисту банківську картку.\n\n"
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
        "✅ Після оплати квитанцію можна надіслати прямо в цей бот.",
        parse_mode=ParseMode.HTML,
    )


async def manager(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Менеджер допоможе з оформленням, розміром та оплатою.",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Зв’язатися з менеджером", url=MANAGER_URL)]]),
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
    await update.message.reply_text(
        "Вкажіть номер замовлення. Якщо його немає — напишіть «Далі».",
        reply_markup=ReplyKeyboardRemove(),
    )
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
    await update.message.reply_text(
        "Вкажіть суму замовлення <b>до знижки</b> цифрами, наприклад: 699",
        parse_mode=ParseMode.HTML,
    )
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
        f"Призначення платежу:\n<code>Оплата за товар, {escape(context.user_data['name'])}</code>\n\n"
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
        await context.bot.send_photo(
            chat_id=PAYMENT_GROUP_ID,
            photo=update.message.photo[-1].file_id,
            caption=caption,
            parse_mode=ParseMode.HTML,
            reply_markup=markup,
        )
    elif update.message.document:
        await context.bot.send_document(
            chat_id=PAYMENT_GROUP_ID,
            document=update.message.document.file_id,
            caption=caption,
            parse_mode=ParseMode.HTML,
            reply_markup=markup,
        )
    else:
        await update.message.reply_text("Надішліть фото, скриншот або PDF-квитанцію.")
        return RECEIPT
    await update.message.reply_text(
        "✅ <b>Квитанцію отримано!</b>\n\n"
        "Дякуємо! Менеджер уже перевіряє вашу оплату.\n\n"
        "Будь ласка, не здійснюйте повторний платіж. Після перевірки ми повідомимо результат у цьому чаті.",
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
    if query.from_user.id != ADMIN_CHAT_ID and query.message.chat_id != PAYMENT_GROUP_ID:
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
    else:
        await context.bot.send_message(
            chat_id=target_user_id,
            text=(
                "⚠️ <b>Оплату поки не знайдено</b>\n\n"
                "Не здійснюйте повторний платіж. Менеджер зв’яжеться з вами для уточнення."
            ),
            parse_mode=ParseMode.HTML,
        )
        status_text = f"⚠️ Позначив(ла): {escape(query.from_user.full_name)}"
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
    conversation = ConversationHandler(
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
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("chatid", chat_id))
    application.add_handler(MessageHandler(filters.Regex("^🎁 Отримати знижку 100 грн$"), payment_offer))
    application.add_handler(MessageHandler(filters.Regex("^🛡️ Чому нам довіряють$"), trust))
    application.add_handler(MessageHandler(filters.Regex("^📦 Доставка та оплата$"), delivery))
    application.add_handler(MessageHandler(filters.Regex("^👨‍💼 Менеджер$"), manager))
    application.add_handler(conversation)
    application.add_handler(CallbackQueryHandler(manager_callback, pattern=r"^(payment_ok|payment_missing):\d+$"))
    application.add_error_handler(error_handler)
    return application


if __name__ == "__main__":
    app = build_application()
    logger.info("Starting HD Sportwear bot")
    app.run_polling(allowed_updates=Update.ALL_TYPES)
