import os
import telebot
from dotenv import load_dotenv
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta, timezone
from flask import Flask, request

# ----------------------------------------------------
# ZEIT-KONFIGURATION & TIMER-FUNKTION
# ----------------------------------------------------

# Die Zeitzone muss festgelegt werden (CET / UTC+1)
# HINWEIS: Auf Render-Servern läuft die Zeit oft auf UTC, daher muss hier die UTC-Zeit verwendet werden
TIMEZONE = timezone.utc 

# STARTDATUM DES ANGEBOTS (Wunsch: 11.12.2025, 00:00:00 UTC)
# Wenn du 00:00:00 CET meinst, müsstest du 23:00:00 UTC wählen, aber UTC ist sicherer
OFFER_START_DATETIME = datetime(2025, 12, 11, 0, 0, 0).replace(tzinfo=TIMEZONE)

# Dauer des Angebots (Wunsch: 9 Tage, 11 Stunden, 19 Minuten)
OFFER_DURATION = timedelta(days=9, hours=11, minutes=19)

# Funktion zur Berechnung der verbleibenden Angebotszeit
def get_time_remaining():
    end_date = OFFER_START_DATETIME + OFFER_DURATION
    now = datetime.now(TIMEZONE)
    remaining = end_date - now
    
    # Prüfen, ob das Angebot abgelaufen ist
    if remaining.total_seconds() <= 0:
        return None 

    days = remaining.days
    seconds = int(remaining.total_seconds())
    
    # Korrekte Berechnung der Stunden und Minuten
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    
    return f"{days} Tage, {hours % 24} Stunden und {minutes % 60} Minuten"
    
# ----------------------------------------------------
# CONFIG (Aus .env geladen) - **ANGEPASST AN DEINE KEYS**
# ----------------------------------------------------
load_dotenv()

# Variablen-Check und Zuweisung, angepasst an DEINE ENV-KEYS (wie du sie mir gesendet hast)
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_CHAT_ID"))   # HIER KORRIGIERT: ADMIN_CHAT_ID
VIP_CHANNEL = int(os.getenv("CHANNEL_ID"))     # HIER KORRIGIERT: CHANNEL_ID
WELCOME_VIDEO_ID = os.getenv("WELCOME_VIDEO_ID") # NEU: Video wird per ID gesendet
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST")

# NEUE ID FÜR DEN PFLICHTKANAL - MUSS IN RENDER HINZUGEFÜGT WERDEN
PUBLIC_CHANNEL = int(os.getenv("PUBLIC_CHANNEL_ID", "-1003451305369")) 

# Zusätzliche Info
CURRENT_PRICE = "50€" 
OFFER_END_PRICE = "85€" 

# Der tatsächliche Einladungslink für die Anzeige an den Benutzer
DISPLAY_CHANNEL_LINK = "t.me/+mKdvOy5tByA3NGRh" 

# ----------------------------------------------------
# WEBHOOK-KONFIGURATION FÜR RENDER
# ----------------------------------------------------
WEBHOOK_PORT = int(os.environ.get('PORT', 5000)) 
WEBHOOK_URL_PATH = f"/{BOT_TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_URL_PATH}"

# ----------------------------------------------------
# ZAHLUNGSDATEN (BLEIBT UNVERÄNDERT)
# ----------------------------------------------------
IBAN = "IE05PPSE99038084774775"
EMPFAENGER = "Emily Hunter"
BIC = "PPSEIE22XXX"
BTC = "bc1q4tywm720a4f8jknur7srnzmh4y87cr7y3xc26c"
USDC_ETH = "0x7d68042B866996d23Fa50a440f782Ef6136DA425"

# Initialisiere den Bot und Flask
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)


# ----------------------------------------------------
# HELPER-FUNKTIONEN (ANGEPASST AN PUBLIC_CHANNEL)
# ----------------------------------------------------

def get_user_name(message):
    name = message.from_user.first_name
    return name if name else "Schatz"

def is_member(user_id):
    try:
        # PRÜFT MITGLIEDSCHAFT IM NEUEN PFLICHTKANAL
        member = bot.get_chat_member(PUBLIC_CHANNEL, user_id) 
        return member.status in ["member", "administrator", "creator"]
    except Exception:
        return False
        
def get_current_price_text():
    time_left = get_time_remaining()
    current_price = CURRENT_PRICE if time_left else OFFER_END_PRICE
    return current_price

# ----------------------------------------------------
# MARKUP-GENERIERUNG
# ----------------------------------------------------
# ... (MARKUP-FUNKTIONEN BLEIBEN GLEICH) ...

# ----------------------------------------------------
# CALLBACK HANDLER
# ----------------------------------------------------

@bot.callback_query_handler(func=lambda call: call.data.startswith('pay_'))
def callback_payment_options(call):
    bot.answer_callback_query(call.id, "Öffne Zahlungsinfos... 💖")
    
    current_price = get_current_price_text() # NEU: Preis abrufen

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("⬅️ Zurück zu den Optionen", callback_data="back_to_pay_options"))

    if call.data == "pay_bank":
        text_de = (
            f"💸 Bank Überweisung ({current_price}) – Für unsere diskrete Abwicklung:\n\n" # NEU: Preis hinzugefügt
            f"IBAN: `{IBAN}`\n"
            f"Empfänger: `{EMPFAENGER}`\n"
            f"BIC: `{BIC}`\n\n"
            "Wichtig: Bitte gib bei der Banküberweisung als Verwendungszweck unbedingt deinen Telegram-Benutzernamen an, damit ich dich zuordnen kann! ❤️"
        )
    elif call.data == "pay_crypto":
        text_de = (
            f"🪙 Krypto-Liebe ({current_price}) – Schnell und anonym:\n\n" # NEU: Preis hinzugefügt
            f"Bitcoin: `{BTC}`\n"
            f"USDC / ETH: `{USDC_ETH}`"
        )
    elif call.data == "pay_paysafe":
        text_de = (
            f"💳 PaySafe Code ({current_price}) – Ganz unkompliziert:\n\n" # NEU: Preis hinzugefügt
            "Du kannst mir den PaySafe Code einfach direkt hier im Chat schicken. So einfach ist das! 💋"
        )
    else:
        text_de = "Entschuldigung, diese Option ist mir nicht bekannt."

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=text_de,
        parse_mode="Markdown",
        reply_markup=markup
    )
    
# ... (REST DER CALLBACK HANDLER BLEIBT GLEICH) ...

# ----------------------------------------------------
# ZAHLUNGSNACHWEIS HANDLING (mit Admin-Benachrichtigung & User-Info)
# ----------------------------------------------------

@bot.message_handler(content_types=["photo", "document"])
def handle_proof(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    # NEU: Prüfe, ob der Benutzer im öffentlichen Kanal ist
    if not is_member(user_id):
        bot.send_message(
            chat_id,
            f"Halt, stopp! Bevor du den Nachweis sendest, tritt bitte zuerst meinem öffentlichen Kanal bei:\n👉 {DISPLAY_CHANNEL_LINK}" 
        )
        return

    bot.send_message(
        chat_id,
        "Ist diese Datei dein ZAHLUNGSNACHWEIS? Bitte einmal bestätigen, damit ich es sofort an meinen Admin weiterleiten kann! 💖",
        reply_markup=generate_proof_confirmation_markup(chat_id, message.message_id)
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('confirm_proof:'))
def confirm_proof_callback(call):
    _, proof_chat_id, proof_message_id = call.data.split(':')
    proof_chat_id = int(proof_chat_id)
    proof_message_id = int(proof_message_id)
    
    # NEU: 1. User-Informationen abrufen
    user_data = bot.get_chat(proof_chat_id)
    
    if user_data.username:
        source_info = f"@{user_data.username}"
    else:
        # Fallback: Chat ID
        source_info = f"Chat ID: `{user_data.id}`"
        
    # NEU: 2. Caption/Unterschrift für den Admin erstellen
    admin_caption = f"🚨 Money Came 💸 | {source_info}"

    # 3. Bestätigung beim Benutzer senden (Bleibt gleich)
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="Vielen Dank für deine Bestätigung! Der Nachweis wird nun geprüft. ✅",
    )
    
    # NEU: 4. Nachweis an den Admin weiterleiten (mit neuem Text VOR dem Forward)
    bot.send_message(
        ADMIN_ID, 
        admin_caption, 
        parse_mode="Markdown"
    )
    bot.forward_message(ADMIN_ID, proof_chat_id, proof_message_id)

    # 5. Bestätigung und Video an den Benutzer senden (Bleibt gleich)
    confirmation_text = (
        "Juhu! Danke dir, mein Schatz! 🌸🥰\n"
        "Ich habe deinen Zahlungsnachweis bekommen und sofort ganz schnell an meinen Admin weitergeleitet.\n"
        "Er prüft das jetzt ganz in Ruhe und meldet sich innerhalb der nächsten 5 MINUTEN persönlich bei dir! Freu dich! 💗\n\n"
        "Hier ist schon mal dein kleines, heißes Begrüßungsvideo 🎀✨"
    )
    bot.send_message(call.message.chat.id, confirmation_text)

    # WICHTIGE KORREKTUR: Senden per ID statt per Dateipfad
    try:
        if WELCOME_VIDEO_ID:
            bot.send_video(call.message.chat.id, WELCOME_VIDEO_ID)
        else:
            bot.send_message(call.message.chat.id, "Fehler: Die Video-ID fehlt im Server-Setup. Bitte wende dich an den Support!")
    except Exception as e:
        # HINWEIS: Hier fangen wir den Fehler ab, falls die ID ungültig ist
        print(f"Fehler beim Senden des Videos (ID: {WELCOME_VIDEO_ID}): {e}")
        bot.send_message(call.message.chat.id, "Entschuldigung, beim Senden des Videos gab es ein Problem.")


@bot.callback_query_handler(func=lambda call: call.data == "cancel_proof")
def cancel_proof_callback(call):
# ... (bleibt gleich) ...
# ... (REST DER FUNKTIONEN BLEIBT GLEICH) ...

# ----------------------------------------------------
# START BOT
# ----------------------------------------------------
if __name__ == '__main__':
    # Ausführung der Webhook-Startlogik
    start_webhook()
