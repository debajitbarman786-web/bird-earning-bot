import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

TOKEN = os.getenv("BOT_TOKEN")

# शुरुआती डेमो: बैलेंस अभी मेमोरी में रखा जाता है।
# बाद में इसे PostgreSQL डेटाबेस से जोड़ेंगे।
balances = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    balances.setdefault(user.id, 0)

    keyboard = [
        [InlineKeyboardButton("🎮 Play Game", callback_data="play")],
        [InlineKeyboardButton("🪙 My Balance", callback_data="balance")],
        [InlineKeyboardButton("👥 Referral", callback_data="referral")],
    ]

    await update.message.reply_text(
        f"नमस्ते {user.first_name}! 🐦\n\n"
        "Bird Earning Bot में आपका स्वागत है!\n"
        "गेम और रिवॉर्ड सिस्टम जल्द उपलब्ध होंगे।",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start - बॉट शुरू करें\n"
        "/balance - अपना बैलेंस देखें\n"
        "/help - मदद प्राप्त करें"
    )


async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    coins = balances.get(user.id, 0)

    await update.effective_message.reply_text(
        f"🪙 आपका बैलेंस: {coins} कॉइन्स"
    )


def main():
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN environment variable सेट नहीं है।")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("balance", balance))

    print("Bot शुरू हो रहा है...")
    app.run_polling()


if __name__ == "__main__":
    main()
