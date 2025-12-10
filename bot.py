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
# Wichtig: ADMIN_ID sollte die NUMERISCHE ID des Admins sein.
ADMIN_ID = int(os.getenv("ADMIN_ID"))
# Wichtig: VIP_CHANNEL sollte der @username des Kanals sein (z.B. "@ChayaVIP")
VIP_CHANNEL = os.getenv("VIP_CHANNEL")
WELCOME_VIDEO_PATH = "welcome.mp4" # Stelle sicher, dass diese Datei im selben Verzeichnis liegt

# Zusätzliche Info
PRICE_INFO = "50€ für permanenten Zugriff"

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
        # VIP_CHANNEL muss hier der @username sein, damit get_chat_member funktioniert
        member = bot.get_chat_member(VIP_CHANNEL, user_id)
        # Überprüfe, ob der Benutzer den Status "member", "administrator" oder "creator" hat
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        print(f"Fehler beim Überprüfen der Kanalmitgliedschaft: {e}")
        return False


# ----------------------------------------------------
# MARKUP-GENERIERUNG (Für die Haupt-Zahlungsoptionen)
# ----------------------------------------------------
def generate_pay_options_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(
        InlineKeyboardButton("🏦 Bank Zahlung", callback_data="pay_bank"),
        InlineKeyboardButton("🪙 Krypto", callback_data="pay_crypto"),
        InlineKeyboardButton("💳 PaySafe Code", callback_data="pay_paysafe")
    )
    return markup


# ----------------------------------------------------
# /start COMMAND
# Handler für den /start Befehl
# ----------------------------------------------------
@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id

    # Erstelle den korrekten t.me Link aus dem @username für die Anzeige
    channel_link_for_display = f"t.me/{VIP_CHANNEL.lstrip('@')}"

    # Überprüfe, ob der Benutzer Mitglied des VIP-Kanals ist
    if not is_member(user_id):
        # Nachricht, wenn der Benutzer NICHT Mitglied ist
        text_de = (
            "Hey mein Lieber 🌸💖\n"
            "wenn du in meine VIP-Gruppe möchtest, musst du zuerst diesem Kanal beitreten:\n\n"
            f"👉 {channel_link_for_display}\n\n" # Hier wird der t.me Link verwendet
            f"Der Zugang kostet nur {PRICE_INFO}.\n" # Preisinformation hinzugefügt
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
        "Falls du erst bezahlen musst, nutze einfach /pay"
    )
    bot.send_message(message.chat.id, start_text_de)


# ----------------------------------------------------
# /pay COMMAND (Hauptbefehl für Zahlungsoptionen)
# ----------------------------------------------------
@bot.message_handler(commands=["pay"])
def pay_options(message):
    bot.send_message(
        message.chat.id,
        f"Wähle deine bevorzugte Zahlungsmethode für {PRICE_INFO}:", # Preis hier auch hinzufügen
        reply_markup=generate_pay_options_markup()
    )


# ----------------------------------------------------
# /support COMMAND
# Handler für den /support Befehl
# ----------------------------------------------------
@bot.message_handler(commands=["support"])
def support(message):
    support_text_de = (
        "Bitte schreibe eine kurze Nachricht an @ProHvnter mit deinem Anliegen.\n"
        "Er wird sich schnellstmöglich um dich kümmern!"
    )
    bot.send_message(message.chat.id, support_text_de)


# ----------------------------------------------------
# /info COMMAND
# Handler für den /info Befehl
# ----------------------------------------------------
@bot.message_handler(commands=["info"])
def info(message):
    info_text_de = (
        "Hey Süßer 💖\n"
        f"hier hast du die Möglichkeit, Zugang zu meiner exklusiven VIP-Gruppe zu kaufen! Der Zugang kostet nur {PRICE_INFO}. ✨\n\n" # Preis hier auch hinzufügen
        "Ich bin Emily, 19 Jahre alt, und ich liebe es, 18+ Videos zu drehen. "
        "In meiner VIP-Gruppe findest du meine heißesten Inhalte und vieles mehr! 🔥\n\n"
        "Nutze /pay, um deine Zahlungsmethode zu wählen und bald dabei zu sein. 🥰"
    )
    bot.send_message(message.chat.id, info_text_de)


# ----------------------------------------------------
# CALLBACK QUERY HANDLER (Reagiert auf Button-Klicks für Zahlungsdetails)
# ----------------------------------------------------
@bot.callback_query_handler(func=lambda call: call.data.startswith('pay_'))
def callback_payment_options(call):
    bot.answer_callback_query(call.id) # Bestätigt den Button-Klick

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("⬅️ Zurück zu den Optionen", callback_data="back_to_pay_options"))

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
            f"Bitcoin: `{BTC}`\n"
            f"USDC / ETH: `{USDC_ETH}`"
        )
    elif call.data == "pay_paysafe":
        text_de = (
            "💸 PaySafe Code:\n\n"
            "Du kannst uns einfach den PaySafe Code direkt im Chat schicken."
        )
    else:
        text_de = "Entschuldigung, diese Option ist mir nicht bekannt."

    # Nachricht bearbeiten, um die neuen Buttons anzuzeigen
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=text_de,
        parse_mode="Markdown",
        reply_markup=markup
    )


# ----------------------------------------------------
# CALLBACK QUERY HANDLER (Reagiert auf "Zurück"-Button)
# ----------------------------------------------------
@bot.callback_query_handler(func=lambda call: call.data == "back_to_pay_options")
def callback_back_to_options(call):
    bot.answer_callback_query(call.id) # Bestätigt den Button-Klick

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"Wähle deine bevorzugte Zahlungsmethode für {PRICE_INFO}:", # Preis hier auch hinzufügen
        reply_markup=generate_pay_options_markup()
    )


# ----------------------------------------------------
# ZAHLUNGSNACHWEIS HANDLING
# Handler für Fotos und Dokumente (Zahlungsnachweise)
# ----------------------------------------------------
@bot.message_handler(content_types=["photo", "document"])
def handle_proof(message):
    user_id = message.from_user.id

    # Erstelle den korrekten t.me Link aus dem @username für die Fehlermeldung
    channel_link_for_display = f"t.me/{VIP_CHANNEL.lstrip('@')}"

    # Überprüfe erneut die Kanalmitgliedschaft, bevor der Nachweis bearbeitet wird
    if not is_member(user_id):
        bot.send_message(
            message.chat.id,
            f"Bitte tritt zuerst dem Kanal bei:\n👉 {channel_link_for_display}"
        )
        return

    # Leite den Zahlungsnachweis an den Admin weiter
    bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)

    # Konsolidierte Bestätigungs- und Abschlussnachricht an den Benutzer
    confirmation_text = (
        "Danke dir mein Lieber 🌸🥰\n"
        "ich habe deinen Zahlungsnachweis bekommen und schon weitergeleitet.\n"
        "Der Admin prüft deinen Nachweis jetzt ganz in Ruhe und meldet sich innerhalb von 5 Minuten bei dir 💗\n\n"
        "Hier ist erstmal dein kleines Begrüßungsvideo 🎀✨"
    )
    bot.send_message(message.chat.id, confirmation_text)

    # Sende das Begrüßungsvideo
    try:
        with open(WELCOME_VIDEO_PATH, "rb") as video:
            bot.send_video(message.chat.id, video)
    except FileNotFoundError:
        bot.send_message(message.chat.id, "Entschuldigung, das Begrüßungsvideo konnte nicht gefunden werden.")
    except Exception as e:
        bot.send_message(message.chat.id, f"Fehler beim Senden des Videos: {e}")


# ----------------------------------------------------
# WENN ER TEXT SENDET (Fallback-Handler)
# Dieser Handler fängt alle Nachrichten ab, die keine Befehle, Fotos oder Dokumente sind
# ----------------------------------------------------
@bot.message_handler(func=lambda m: True)
def fallback(message):
    bot.send_message(
        message.chat.id,
        "Hey Süßer 🌺\n"
        "ich brauche bitte ein Foto oder Dokument als Zahlungsnachweis,\n"
        "damit ich alles richtig prüfen kann 💖✨\n\n"
        "Falls du zuerst bezahlen möchtest: /pay"
    )


# ----------------------------------------------------
# START BOT
# Starte den Bot und lasse ihn auf Nachrichten pollen
# ----------------------------------------------------
print("Bot startet...")
bot.polling(none_stop=True)
