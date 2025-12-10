import os
import telebot
from dotenv import load_dotenv
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Lade Umgebungsvariablen aus der .env-Datei
load_dotenv()

# ----------------------------------------------------
# CONFIG (Aus .env geladen)
# ----------------------------------------------------
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))  # ADMIN_ID muss als Integer gespeichert werden
VIP_CHANNEL = os.getenv("VIP_CHANNEL")
WELCOME_VIDEO_PATH = "welcome.mp4" # Stelle sicher, dass diese Datei im selben Verzeichnis liegt

# ----------------------------------------------------
# ZAHLUNGSDATEN (Direkt im Code)
# ----------------------------------------------------
IBAN = "IE05PPSE99038084774775"
EMPFAENGER = "Emily Hunter"
BIC = "PPSEIE22XXX"
BTC = "bc1q4tywm720a4f8jknur7srnzmh4y87cr7y3xc26c"
USDC_ETH = "0x7d68042B866996d23Fa50a440f782Ef6136DA425"

# Initialisiere den Bot
bot = telebot.TeleBot(BOT_TOKEN)


# ----------------------------------------------------
# HELPER → KANALCHECK
# Funktion zum Überprüfen, ob ein Benutzer Mitglied des VIP-Kanals ist
# ----------------------------------------------------
def is_member(user_id):
    try:
        member = bot.get_chat_member(VIP_CHANNEL, user_id)
        # Überprüfe, ob der Benutzer den Status "member", "administrator" oder "creator" hat
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        print(f"Fehler beim Überprüfen der Kanalmitgliedschaft: {e}")
        return False


# ----------------------------------------------------
# /start COMMAND
# Handler für den /start Befehl
# ----------------------------------------------------
@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id

    # Überprüfe, ob der Benutzer Mitglied des VIP-Kanals ist
    if not is_member(user_id):
        text_de = (
            "Hey mein Lieber 🌸💖\n"
            "wenn du in meine VIP-Gruppe möchtest, musst du zuerst diesem Kanal beitreten:\n\n"
            f"👉 {@ChayaVIP}\n\n"
            "Tritt kurz bei und komm dann wieder hierher zurück.\n"
            "Ich freue mich auf dich ✨"
        )
        bot.send_message(message.chat.id, text_de)
        return

    # Wenn der Benutzer Mitglied ist, sende die Begrüßungsnachricht
    start_text_de = (
        "Hey mein Lieber 💕\n"
        "schön, dass du hier bist! 🌷✨\n\n"
        "Bitte sende mir jetzt deinen Zahlungsnachweis\n"
        "(z.B. Screenshot oder Dokument).  \n"
        "Ich kümmere mich sofort um alles Weitere 🤍\n\n"
        "Falls du erst bezahlen musst, nutze einfach /pay" # Befehl hier auch angepasst
    )
    bot.send_message(message.chat.id, start_text_de)


# ----------------------------------------------------
# /pay COMMAND (Neuer Befehl für Zahlungsoptionen)
# ----------------------------------------------------
@bot.message_handler(commands=["pay"])
def pay_options(message):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1 # Eine Spalte für die Buttons
    markup.add(
        InlineKeyboardButton("🏦 Bank Zahlung", callback_data="pay_bank"),
        InlineKeyboardButton("🪙 Krypto", callback_data="pay_crypto"),
        InlineKeyboardButton("💳 PaySafe Code", callback_data="pay_paysafe")
    )
    bot.send_message(message.chat.id, "Wähle deine bevorzugte Zahlungsmethode:", reply_markup=markup)


# ----------------------------------------------------
# CALLBACK QUERY HANDLER (Reagiert auf Button-Klicks)
# ----------------------------------------------------
@bot.callback_query_handler(func=lambda call: call.data.startswith('pay_'))
def callback_payment_options(call):
    bot.answer_callback_query(call.id) # Bestätigt den Button-Klick

    if call.data == "pay_bank":
        text_de = (
            "💸 Bank Überweisung:\n\n"
            f"IBAN: `{IBAN}`\n"
            f"Empfänger: `{EMPFAENGER}`\n"
            f"BIC: `{BIC}`\n\n"
            "Wichtig: Bitte gib bei der Banküberweisung als Verwendungszweck deinen Telegram-Benutzernamen ein!"
        )
    elif call.data == "pay_crypto":
        text_de = (
            "💸 Krypto-Adressen:\n\n"
            f"Bitcoin (16-stellig): `{BTC}`\n"
            f"USDC / ETH: `{USDC_ETH}`"
        )
    elif call.data == "pay_paysafe":
        text_de = (
            "💸 PaySafe Code:\n\n"
            "Du kannst uns einfach den PaySafe Code direkt im Chat schicken."
        )
    else:
        text_de = "Entschuldigung, diese Option ist mir nicht bekannt."

    bot.send_message(call.message.chat.id, text_de, parse_mode="Markdown")


# ----------------------------------------------------
# ZAHLUNGSNACHWEIS HANDLING
# Handler für Fotos und Dokumente (Zahlungsnachweise)
# ----------------------------------------------------
@bot.message_handler(content_types=["photo", "document"])
def handle_proof(message):
    user_id = message.from_user.id

    # Überprüfe erneut die Kanalmitgliedschaft, bevor der Nachweis bearbeitet wird
    if not is_member(user_id):
        bot.send_message(
            message.chat.id,
            f"Bitte tritt zuerst dem Kanal bei:\n👉 {VIP_CHANNEL}"
        )
        return

    # Leite den Zahlungsnachweis an den Admin weiter
    bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)

    # Bestätigungsnachricht an den Benutzer
    bot.send_message(
        message.chat.id,
        "Danke dir mein Lieber 🌸🥰\n"
        "ich habe deinen Zahlungsnachweis bekommen und schon weitergeleitet.\n\n"
        "Hier ist erstmal dein kleines Begrüßungsvideo 🎀✨"
    )

    # Sende das Begrüßungsvideo
    try:
        with open(WELCOME_VIDEO_PATH, "rb") as video:
            bot.send_video(message.chat.id, video)
    except FileNotFoundError:
        bot.send_message(message.chat.id, "Entschuldigung, das Begrüßungsvideo konnte nicht gefunden werden.")
    except Exception as e:
        bot.send_message(message.chat.id, f"Fehler beim Senden des Videos: {e}")


    # Abschlussnachricht an den Benutzer
    bot.send_message(
        message.chat.id,
        "Alles klar mein Schatz 🌼\n"
        "der Admin prüft deinen Nachweis jetzt ganz in Ruhe\n"
        "und meldet sich gleich bei dir 💗"
    )


# ----------------------------------------------------
# WENN ER TEXT SENDET (Fallback-Handler)
# Dieser Handler fängt alle Nachrichten ab, die keine Befehle, Fotos oder Dokumente sind
# ----------------------------------------------------
@bot.message_handler(func=lambda m: True)
def fallback(message):
    bot.send_message(
        message.chat.id,
        "Hey Süßer 🌺\n"
        "ich brauche bitte ein Foto als Zahlungsnachweis,\n"
        "damit ich alles richtig prüfen kann 💖✨\n\n"
        "Falls du zuerst bezahlen möchtest: /pay" # Befehl hier auch angepasst
    )


# ----------------------------------------------------
# START BOT
# Starte den Bot und lasse ihn auf Nachrichten pollen
# ----------------------------------------------------
print("Bot startet...")
bot.polling(none_stop=True)
