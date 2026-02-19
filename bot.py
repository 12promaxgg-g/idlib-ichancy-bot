import sqlite3
import random
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.getenv("8506689609:AAFtVMoLq4vjQSJkJD2WJcUf50f-CFNbjaA")
ADMIN_ID = 6184030488
BOT_USERNAME = "idlib_ichancy_bot"

conn = sqlite3.connect("bot.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    balance INTEGER DEFAULT 100,
    invited_by INTEGER,
    invites INTEGER DEFAULT 0
)
""")
conn.commit()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = cursor.fetchone()

    if not user:
        invited_by = None
        if context.args:
            invited_by = int(context.args[0])

        cursor.execute("INSERT INTO users (user_id, invited_by) VALUES (?,?)",
                       (user_id, invited_by))
        conn.commit()

        if invited_by and invited_by != user_id:
            cursor.execute("UPDATE users SET balance = balance + 30, invites = invites + 1 WHERE user_id=?",
                           (invited_by,))
            conn.commit()

    invite_link = f"https://t.me/{BOT_USERNAME}?start={user_id}"

    await update.message.reply_text(
        f"👋 أهلاً بك في بوت idlib ichancy\n\n"
        f"💰 رصيدك: 100 نقطة\n\n"
        f"🔗 رابط دعوتك:\n{invite_link}"
    )

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    cursor.execute("SELECT balance, invites FROM users WHERE user_id=?", (user_id,))
    result = cursor.fetchone()

    if result:
        await update.message.reply_text(
            f"💰 رصيدك: {result[0]} نقطة\n"
            f"👥 عدد الدعوات: {result[1]}"
        )

async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    cursor.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
    result = cursor.fetchone()

    if not result or result[0] < 10:
        await update.message.reply_text("❌ تحتاج 10 نقاط للعب")
        return

    win = random.choice([True, False])

    if win:
        cursor.execute("UPDATE users SET balance = balance + 25 WHERE user_id=?",
                       (user_id,))
        await update.message.reply_text("🎉 ربحت 25 نقطة!")
    else:
        cursor.execute("UPDATE users SET balance = balance - 10 WHERE user_id=?",
                       (user_id,))
        await update.message.reply_text("😢 خسرت 10 نقاط")

    conn.commit()

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    await update.message.reply_text(f"📊 عدد المستخدمين: {count}")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("balance", balance))
app.add_handler(CommandHandler("play", play))
app.add_handler(CommandHandler("stats", stats))
app.run_polling()
