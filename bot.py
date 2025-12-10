import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ----------------------------------------------------
# CONFIG
# ----------------------------------------------------
BOT_TOKEN = "DEIN_TELEGRAM_BOT_TOKEN"
ADMIN_ID = 123456789                # Deine Telegram-ID
VIP_CHANNEL = "@chayavip"           # Kanal, den Nutzer betreten müssen
WELCOME_VIDEO_PATH = "welcome.mp4"  # Dein Begrüßungsvideo

bot = telebot.TeleBot(BOT_TOKEN)

# ----------------------------------------------------
# HELPER → KANALCHECK
# ----------------------------------------------------
def is_member(user_id):
    try:
        member = bot.get_chat_member(VIP_CHANNEL, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# ----------------------------------------------------
# /start COMMAND
# ----------------------------------------------------
@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id

    if not is_member(user_id):
        text_de = (
            "Hey mein Lieber 🌸💖\n"
            "wenn du in meine VIP-Gruppe möchtest, musst du zuerst diesem Kanal beitreten:\n\n"
            f"👉 {VIP_CHANNEL}\n\n"
            "Tritt kurz bei und komm dann wieder hierher zurück.\n"
            "Ich freue mich auf dich ✨"
        )
        bot.send_message(message.chat.id, text_de)
        return

    # Falls er im Kanal ist → normal starten
    start_text_de = (
        "Hey mein Lieber 💕\n"
        "schön, dass du hier bist! 🌷✨\n\n"
        "Bitte sende mir jetzt deinen Zahlungsnachweis\n"
        "(z.B. Screenshot oder Dokument).  \n"
        "Ich kümmere mich sofort um alles Weitere 🤍"
    )
    bot.send_message(message.chat.id, start_text_de)

# ----------------------------------------------------
# ZAHLUNGSNACHWEIS HANDLING (Fotos / Dokumente)
# ----------------------------------------------------
@bot.message_handler(content_types=["photo", "document"])
def handle_proof(message):
    user_id = message.from_user.id

    if not is_member(user_id):
        bot.send_message(
            message.chat.id,
            f"Bitte tritt zuerst dem Kanal bei:\n👉 {VIP_CHANNEL}"
        )
        return

    # Weiterleiten an Admin
    bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)

    # Nutzer informieren
    bot.send_message(
        message.chat.id,
        "Danke dir mein Lieber 🌸🥰\n"
        "ich habe deinen Zahlungsnachweis bekommen und schon weitergeleitet.\n\n"
        "Hier ist erstmal dein kleines Begrüßungsvideo 🎀✨"
    )

    # Begrüßungsvideo senden
    video = open(WELCOME_VIDEO_PATH, "rb")
    bot.send_video(message.chat.id, video)
    video.close()

    bot.send_message(
        message.chat.id,
        "Alles klar mein Schatz 🌼\n"
        "der Admin prüft deinen Nachweis jetzt ganz in Ruhe\n"
        "und meldet sich gleich bei dir 💗"
    )

# ----------------------------------------------------
# WENN ER TEXT SENDet
# ----------------------------------------------------
@bot.message_handler(func=lambda m: True)
def fallback(message):
    bot.send_message(
        message.chat.id,
        "Hey Süßer 🌺\n"
        "ich brauche bitte ein Foto oder Dokument als Zahlungsnachweis,\n"
        "damit ich alles richtig prüfen kann 💖✨"
    )

# ----------------------------------------------------
# START BOT
# ----------------------------------------------------
bot.polling(none_stop=True)
