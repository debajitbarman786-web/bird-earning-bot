import os
import logging
from collections import defaultdict

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# Set these in your hosting environment's secret variables.
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_USER_ID = int(os.getenv("ADMIN_USER_ID", "0"))

# Demo settings
COINS_PER_RUPEE = 1000
REWARD_PER_SCORE = 1

# Temporary in-memory storage.
# A database is needed to preserve balances after restarts.
balances = defaultdict(int)
referrals = {}
played_games = 0

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def is_admin(user_id: int) -> bool:
    return ADMIN_USER_ID != 0 and user_id == ADMIN_USER_ID


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    balances.setdefault(user.id, 0)

    keyboard = [
        [InlineKeyboardButton("🎮 Play Demo", callback_data="play")],
        [InlineKeyboardButton("💰 My Balance", callback_data="balance")],
        [InlineKeyboardButton("🤝 Referral", callback_data="referral")],
    ]

    await update.message.reply_text(
        f"🐦 Welcome, {user.first_name}!\n\n"
        "Welcome to Bird Earning Bot.\n"
        "Play is currently a demo; no real money is paid.\n\n"
        "Choose an option below.",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📘 Commands\n"
        "/start - Open the bot\n"
        "/myid - Show your Telegram User ID\n"
        "/balance - Check your coins\n"
        "/play SCORE - Demo reward using a score\n"
        "/referral - Get your referral link\n"
        "/admin - Admin commands (admin only)\n\n"
        "Example: /play 20"
    )


async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"Your Telegram User ID: {update.effective_user.id}\n"
        "Keep this ID private if you prefer."
    )


async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await update.message.reply_text(
        f"💰 Your balance: {balances[user_id]} coins\n"
        f"Demo conversion: {COINS_PER_RUPEE} coins = ₹1.\n"
        "This is not a cash balance."
    )


async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global played_games

    user_id = update.effective_user.id

    if not context.args:
        await update.message.reply_text(
            "Send a demo score like this:\n/play 20\n\n"
            "This command is only a test, not a verified game."
        )
        return

    try:
        score = int(context.args[0])
    except ValueError:
        await update.message.reply_text("Score must be a whole number.")
        return

    if score < 0 or score > 10000:
        await update.message.reply_text("Score must be between 0 and 10000.")
        return

    reward = score * REWARD_PER_SCORE
    balances[user_id] += reward
    played_games += 1

    await update.message.reply_text(
        f"🐦 Demo score: {score}\n"
        f"🪙 Demo reward: {reward} coins\n"
        f"💰 New balance: {balances[user_id]} coins\n\n"
        "Note: This is a test command, not a verified game result."
    )


async def referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot_username = context.bot.username
    user_id = update.effective_user.id
    link = f"https://t.me/{bot_username}?start={user_id}"

    await update.message.reply_text(
        "🤝 Your referral link:\n"
        f"{link}\n\n"
        "Referral tracking and referral rewards are not enabled yet."
    )


async def button_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()

    if query.data == "play":
        await query.message.reply_text(
            "🎮 Game demo\n\n"
            "To test rewards, send /play 20\n"
            "The real Flappy Bird game is not connected yet."
        )

    elif query.data == "balance":
        user_id = query.from_user.id
        await query.message.reply_text(
            f"💰 Balance: {balances[user_id]} coins"
        )

    elif query.data == "referral":
        bot_username = context.bot.username
        user_id = query.from_user.id
        link = f"https://t.me/{bot_username}?start={user_id}"
        await query.message.reply_text(
            f"🤝 Your referral link:\n{link}\n"
            "Referral rewards are not enabled yet."
        )


async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Admin only.")
        return

    await update.message.reply_text(
        "🛠 Admin Commands\n\n"
        "/stats - Bot statistics\n"
        "/setreward NUMBER - Coins per demo score point\n"
        "/addcoins USER_ID AMOUNT - Add demo coins\n"
        "/setrate NUMBER - Set coins per ₹1\n\n"
        "Example: /setreward 2\n"
        "Example: /addcoins 123456789 500\n"
        "Example: /setrate 1000"
    )


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Admin only.")
        return

    await update.message.reply_text(
        f"📊 Demo Stats\n"
        f"Users seen: {len(balances)}\n"
        f"Games tested: {played_games}\n"
        f"Total demo coins: {sum(balances.values())}\n"
        f"Reward per score point: {REWARD_PER_SCORE}\n"
        f"Coins per ₹1 (display only): {COINS_PER_RUPEE}"
    )


async def setreward(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    global REWARD_PER_SCORE

    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Admin only.")
        return

    try:
        value = int(context.args[0])
        if not 0 <= value <= 1000:
            raise ValueError
    except (IndexError, ValueError):
        await update.message.reply_text(
            "Use: /setreward 2\nChoose a whole number from 0 to 1000."
        )
        return

    REWARD_PER_SCORE = value
    await update.message.reply_text(
        f"✅ Demo reward set to {REWARD_PER_SCORE} coins per score point."
    )


async def setrate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global COINS_PER_RUPEE

    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Admin only.")
        return

    try:
        value = int(context.args[0])
        if not 1 <= value <= 100000000:
            raise ValueError
    except (IndexError, ValueError):
        await update.message.reply_text(
            "Use: /setrate 1000\nEnter a positive whole number."
        )
        return

    COINS_PER_RUPEE = value
    await update.message.reply_text(
        f"✅ Display conversion set to {COINS_PER_RUPEE} coins per ₹1.\n"
        "This does not transfer or pay real money."
    )


async def addcoins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Admin only.")
        return

    try:
        target_id = int(context.args[0])
        amount = int(context.args[1])
        if amount <= 0 or amount > 100000000:
            raise ValueError
    except (IndexError, ValueError):
        await update.message.reply_text(
            "Use: /addcoins USER_ID AMOUNT\n"
            "Example: /addcoins 123456789 500"
        )
        return

    balances[target_id] += amount
    await update.message.reply_text(
        f"✅ Added {amount} demo coins to user {target_id}.\n"
        f"New demo balance: {balances[target_id]}"
    )


def main():
    if not BOT_TOKEN:
        raise RuntimeError(
            "BOT_TOKEN is missing. Set it in your hosting environment."
        )

    if ADMIN_USER_ID == 0:
        logger.warning(
            "ADMIN_USER_ID is not set. Admin commands will be unavailable."
        )

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("myid", myid))
    app.add_handler(CommandHandler("balance", balance))
    app.add_handler(CommandHandler("play", play))
    app.add_handler(CommandHandler("referral", referral))
    app.add_handler(CommandHandler("admin", admin))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("setreward", setreward))
    app.add_handler(CommandHandler("setrate", setrate))
    app.add_handler(CommandHandler("addcoins", addcoins))
    app.add_handler(CallbackQueryHandler(button_handler))

    logger.info("Bot started.")
    app.run_polling()


if __name__ == "__main__":
    main()
