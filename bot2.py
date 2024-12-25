from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from deep_translator import GoogleTranslator
import os

# Start komandasini yaratish
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_first_name = update.message.from_user.first_name
    text = f"Salom {user_first_name}! Iltimos, quyidagi tugmalar orqali davom eting:"
    
    # Tugmalar
    keyboard = [
        [InlineKeyboardButton("🔗 Kanalga obuna bo'lish", url="https://t.me/akfaeshik_derazalar")],
        [InlineKeyboardButton("✅ Obunani tekshirish", callback_data="subscribed")],
        [InlineKeyboardButton("🔄 Boshqa do'stlarga yuborish", switch_inline_query="")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text, reply_markup=reply_markup)

# Obunani tekshirish
async def check_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    channel_username = "@akfaeshik_derazalar"

    try:
        member = await context.bot.get_chat_member(channel_username, user_id)
        if member.status in ["member", "administrator", "creator"]:
            context.user_data['is_subscribed'] = True
            await query.edit_message_text(text="✅ Siz kanalga obuna bo'lgansiz! Endi matn yuboring:")
        else:
            context.user_data['is_subscribed'] = False
            await query.edit_message_text(text="❌ Siz hali kanalga obuna bo'lmadingiz. Iltimos, obuna bo'ling.")
    except Exception as e:
        await query.edit_message_text(text="❌ Obuna tekshirishda xatolik yuz berdi. Keyinroq urinib ko'ring.")

# Matnni olish va tarjima tilini tanlash
async def get_text_to_translate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get('is_subscribed', False):
        keyboard = [
            [InlineKeyboardButton("🔗 Kanalga obuna bo'lish", url="https://t.me/akfaeshik_derazalar")],
            [InlineKeyboardButton("✅ Obunani tekshirish", callback_data="subscribed")],
            [InlineKeyboardButton("🔄 Boshqa do'stlarga yuborish", switch_inline_query="")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("❌ Tarjima funksiyasidan foydalanish uchun avval kanalga obuna bo'ling!", reply_markup=reply_markup)
        return

    original_text = update.message.text
    context.user_data['original_text'] = original_text
    
    keyboard = [
        [InlineKeyboardButton("🇬🇧 Ingliz", callback_data="lang_en"),
         InlineKeyboardButton("🇷🇺 Rus", callback_data="lang_ru")],
        [InlineKeyboardButton("🇨🇳 Xitoy", callback_data="lang_zh-CN"),
         InlineKeyboardButton("🇯🇵 Yapon", callback_data="lang_ja")],
        [InlineKeyboardButton("🇹🇷 Turk", callback_data="lang_tr"),
         InlineKeyboardButton("🇩🇪 Nemis", callback_data="lang_de")],
        [InlineKeyboardButton("🇫🇷 Fransuz", callback_data="lang_fr"),
         InlineKeyboardButton("🇪🇸 Ispan", callback_data="lang_es")],
        [InlineKeyboardButton("🇮🇹 Italiya", callback_data="lang_it"),
         InlineKeyboardButton("🇰🇷 Koreys", callback_data="lang_ko")],
        [InlineKeyboardButton("🇸🇦 Arab", callback_data="lang_ar"),
         InlineKeyboardButton("🇮🇳 Hind", callback_data="lang_hi")],
        [InlineKeyboardButton("🇵🇹 Portugaliya", callback_data="lang_pt"),
         InlineKeyboardButton("🇳🇱 Golland", callback_data="lang_nl")],
        [InlineKeyboardButton("🇺🇿 O‘zbek", callback_data="lang_uz")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Qaysi tilga tarjima qilinsin?", reply_markup=reply_markup)

# Tarjima qilish
async def translate_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target_language = query.data.split("_")[1]
    original_text = context.user_data.get('original_text')

    if original_text:
        try:
            translated_text = GoogleTranslator(source='auto', target=target_language).translate(original_text)
            keyboard = [
                [InlineKeyboardButton("🔄 Boshqa do'stlarga yuborish", switch_inline_query=translated_text)]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                text=f"✅ Tarjima: {translated_text}\nYana matn yuboring:",
                reply_markup=reply_markup
            )
        except Exception as e:
            await query.edit_message_text(
                text="❌ Tarjima jarayonida xatolik yuz berdi.",
                reply_markup=query.message.reply_markup
            )
    else:
        await query.edit_message_text(
            text="❌ Matn topilmadi. Iltimos, qayta matn yuboring.",
            reply_markup=query.message.reply_markup
        )

# Botni ishga tushirish
def main():
    token = os.getenv("7843981433:AAGKcQi-lxjoKUDC3IjppCYO4ZoibfFm9nU")  # Tokenni muhiti o'zgaruvchisidan oling
    port = int(os.environ.get("PORT", 5000))  # Portni olish

    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(check_subscription, pattern="^subscribed$"))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_text_to_translate))
    application.add_handler(CallbackQueryHandler(translate_text, pattern="^lang_"))

    # Webhook sozlamalari
    app_url = os.getenv("APP_URL")  # Render tomonidan taqdim etilgan URL
    application.run_webhook(
        listen="0.0.0.0",
        port=port,
        webhook_url=f"{app_url}/{token}"
    )

if __name__ == "__main__":
    main()
    
 
