import os
import telebot
from dotenv import load_dotenv
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta, timezone
# NEU: Flask für Webhooks
from flask import Flask, request

# ----------------------------------------------------
# ZEIT-KONFIGURATION & TIMER-FUNKTION
# ----------------------------------------------------

# Die Zeitzone muss festgelegt werden (CET / UTC+1)
TIMEZONE = timezone(timedelta(hours=1)) 

# STARTDATUM DES ANGEBOTS (Wunsch: 11.12.2025, 00:00:00 Uhr)
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

    # Zeit in Tage, Stunden, Minuten konvertieren
    days = remaining.days
    seconds = int(remaining.total_seconds())
    
    # Korrekte Berechnung der Stunden und Minuten
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    
    return f"{days} Tage, {hours} Stunden und {minutes} Minuten"

# ----------------------------------------------------
# CONFIG (Aus .env geladen)
# ----------------------------------------------------
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
VIP_CHANNEL = int(os.getenv("VIP_CHANNEL", -1003451305369)) 
WELCOME_VIDEO_PATH = "welcome.mp4" 

# Zusätzliche Info
CURRENT_PRICE = "50€" # Aktueller Angebotspreis
OFFER_END_PRICE = "85€" # Preis nach Ablauf der Frist

# Der tatsächliche Einladungslink für die Anzeige an den Benutzer
DISPLAY_CHANNEL_LINK = "t.me/+mKdvOy5tByA3NGRh"

# ----------------------------------------------------
# WEBHOOK-KONFIGURATION FÜR RENDER
# ----------------------------------------------------
# WEBHOOK_HOST MUSS in Render als ENV Variable gesetzt werden (z.B. https://dein-botname.onrender.com)
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST")
WEBHOOK_PORT = int(os.environ.get('PORT', 5000)) 
WEBHOOK_URL_PATH = f"/{BOT_TOKEN}"
# Die volle URL, die Telegram aufruft
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_URL_PATH}"

# ----------------------------------------------------
# ZAHLUNGSDATEN
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
# HELPER-FUNKTIONEN
# ----------------------------------------------------

def get_user_name(message):
    name = message.from_user.first_name
    return name if name else "Schatz"

def is_member(user_id):
    try:
        member = bot.get_chat_member(VIP_CHANNEL, user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        #print(f"Fehler beim Überprüfen der Kanalmitgliedschaft: {e}")
        return False


# ----------------------------------------------------
# MARKUP-GENERIERUNG
# ----------------------------------------------------

def generate_pay_options_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(
        InlineKeyboardButton("🏦 Bank Zahlung", callback_data="pay_bank"),
        InlineKeyboardButton("🪙 Krypto", callback_data="pay_crypto"),
        InlineKeyboardButton("💳 PaySafe Code", callback_data="pay_paysafe"),
        InlineKeyboardButton("⬅️ Zurück zur Info", callback_data="show_info")
    )
    return markup

def generate_info_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(
        InlineKeyboardButton("💕 Lass uns loslegen!", callback_data="show_pay_options")
    )
    return markup

def generate_proof_confirmation_markup(chat_id, message_id):
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("✅ JA, Nachweis senden", callback_data=f"confirm_proof:{chat_id}:{message_id}"),
        InlineKeyboardButton("❌ Abbrechen", callback_data="cancel_proof")
    )
    return markup


# ----------------------------------------------------
# COMMAND HANDLER
# ----------------------------------------------------

@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id
    name = get_user_name(message) 
    
    time_left = get_time_remaining()

    # Wenn der Benutzer NICHT Mitglied ist -> Gekürzte Info + Kanalbeitritt als Zwang
    if not is_member(user_id):
        
        if time_left:
            price_text = (
                f"🎉 Glückwunsch! Du hast das ANGEBOT erwischt!\n"
                f"Der permanente Zugang kostet aktuell nur {CURRENT_PRICE}. Danach sind es {OFFER_END_PRICE}!\n"
                f"⏰ BEEIL DICH! Du hast nur noch {time_left} Zeit! JETZT SICHERN! 💖\n\n"
            )
        else:
            price_text = (
                f"⚠️ Das Angebot ist leider abgelaufen. Der permanente Zugang kostet jetzt {OFFER_END_PRICE}.\n\n"
            )

        text_de = (
            f"Ach, du lieber {name}! Willkommen in meiner süßen Welt! 🌸💖\n\n"
            "In meiner exklusiven VIP-Gruppe warten ÜBER 70 SÜNDHAFT HEISSE VIDEOS auf dich, "
            "und ich telefoniere auch ab und zu mit meinen treuesten Kunden! 🔥📞\n\n"
            f"{price_text}"
            "Damit wir uns von Anfang an verbunden fühlen und du keine meiner süßen Updates verpasst, "
            "tritt bitte kurz meinem ÖFFENTLICHEN KANAL bei:\n"
            f"👉 {DISPLAY_CHANNEL_LINK}\n\n"
            "Komm danach sofort zurück! Ich freu mich auf dich! ✨"
        )
        bot.send_message(message.chat.id, text_de, parse_mode="Markdown")
        return

    # Wenn der Benutzer Mitglied ist (Bereit zur Zahlung)
    start_text_de = (
        f"Hallo mein lieber {name} 💕\n"
        "Toll, dass du dabei bist! Momentan warten über 70 Videos in der VIP-Gruppe darauf, von dir entdeckt zu werden! 🌷✨\n\n"
        "Jetzt fehlt nur noch ein kleiner Schritt, damit ich dich in die VIP-Gruppe schicken kann! \n"
        "Sende mir jetzt bitte nur noch deinen ZAHLUNGSNACHWEIS\n"
        "(am besten als Screenshot oder Dokument).  \n"
        "Ich kümmere mich dann sofort und ganz liebevoll um alles Weitere 🤍\n\n"
        "Falls du noch zahlen möchtest, nutze /pay für alle Optionen."
    )
    bot.send_message(message.chat.id, start_text_de)


@bot.message_handler(commands=["pay"])
def pay_options(message):
    time_left = get_time_remaining()
    current_price = CURRENT_PRICE if time_left else OFFER_END_PRICE

    bot.send_message(
        message.chat.id,
        f"Schatz, wähle einfach, wie du mir den permanenten Zugang für {current_price} sichern möchtest! 🎀",
        reply_markup=generate_pay_options_markup()
    )


@bot.message_handler(commands=["support"])
def support(message):
    support_text_de = (
        "Wenn du eine Frage hast oder Hilfe brauchst, schreibe bitte eine kurze Nachricht an @ProHvnter mit deinem Anliegen.\n"
        "Er wird sich schnellstmöglich um dich kümmern, damit alles reibungslos läuft! 💗"
    )
    bot.send_message(message.chat.id, support_text_de)


@bot.message_handler(commands=["info"])
def info(message):
    time_left = get_time_remaining()

    if time_left:
        price_text = (
            f"🎉 Du hast Glück! Der permanente Zugang kostet aktuell nur {CURRENT_PRICE}.\n"
            f"Der Preis steigt in Kürze auf {OFFER_END_PRICE}!\n"
            f"⏰ BEEIL DICH! Du hast nur noch {time_left} Zeit! JETZT SICHERN! 💖\n\n"
        )
    else:
        price_text = (
            f"⚠️ Das zeitlich begrenzte Angebot ist leider abgelaufen. Der permanente Zugang kostet jetzt {OFFER_END_PRICE}.\n\n"
        )

    info_text_de = (
        "Hallo mein Schatz! Herzlich willkommen in meiner süßen Welt! 🥰\n\n"
        "Ich bin Emily, 19 Jahre alt, und ich stecke all meine Leidenschaft in heiße 18+ Videos! "
        "In meiner exklusiven VIP-Gruppe warten momentan ÜBER 70 SÜNDHAFT HEISSE VIDEOS auf dich! 🔥\n\n"
        "Außerdem findest du dort meine allerheißesten Inhalte und ich telefoniere auch ab und zu mit meinen treuesten Kunden, um eine ganz persönliche Verbindung aufzubauen! 📞💖\n\n"
        f"{price_text}"
        "Du kannst jetzt Zugang zu dieser tollen Community kaufen! "
        "Lass uns Spaß haben! ✨"
    )
    bot.send_message(message.chat.id, info_text_de, reply_markup=generate_info_markup(), parse_mode="Markdown")


@bot.message_handler(commands=["regeln", "rules"])
def rules(message):
    rules_text_de = (
        "Liebe ist Ordnung! Damit wir alle eine wunderschöne Zeit in der VIP-Gruppe haben, beachte bitte diese UNUMGÄNGLICHEN REGELN zur Absicherung unserer Inhalte: ✨\n\n"
        "1. Vertraulichkeit & Rechtliche Schritte (SEHR WICHTIG):\n"
        "Mit dem Kauf des VIP-Zugangs bist du damit einverstanden, dass im Falle einer illegalen Weitergabe meiner Videos folgende Schritte eingeleitet werden:\n"
        "   - Verfolgung: Jede unautorisierte Weitergabe wird lückenlos verfolgt und dokumentiert.\n"
        "   - Datenerfassung: Durch Dritte wird automatisiert deine TELEFONNUMMER erfasst, um deine Identität zweifelsfrei festzustellen.\n"
        "   - Rechtliche Konsequenzen: Es werden umgehend rechtliche Schritte eingeleitet. Dein Zugang wird sofort und permanent gesperrt.\n\n"
        "2. Persönlicher Zugang: Dein VIP-Zugang ist streng persönlich. Teile den Link oder die Inhalte niemals. 🚫\n"
        "3. Respekt: Sei lieb und respektvoll zu mir und anderen Mitgliedern. ❤️\n\n"
        "Wenn du Fragen hast, nutze /support. Danke für dein Verständnis und viel Spaß! 🥰"
    )
    bot.send_message(message.chat.id, rules_text_de)


# ----------------------------------------------------
# CALLBACK HANDLER
# ----------------------------------------------------

@bot.callback_query_handler(func=lambda call: call.data.startswith('pay_'))
def callback_payment_options(call):
    bot.answer_callback_query(call.id, "Öffne Zahlungsinfos... 💖") 

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("⬅️ Zurück zu den Optionen", callback_data="back_to_pay_options"))

    if call.data == "pay_bank":
        text_de = (
            "💸 Bank Überweisung – Für unsere diskrete Abwicklung:\n\n"
            f"IBAN: `{IBAN}`\n"
            f"Empfänger: `{EMPFAENGER}`\n"
            f"BIC: `{BIC}`\n\n"
            "Wichtig: Bitte gib bei der Banküberweisung als Verwendungszweck unbedingt deinen Telegram-Benutzernamen an, damit ich dich zuordnen kann! ❤️"
        )
    elif call.data == "pay_crypto":
        text_de = (
            "🪙 Krypto-Liebe – Schnell und anonym:\n\n"
            f"Bitcoin: `{BTC}`\n"
            f"USDC / ETH: `{USDC_ETH}`"
        )
    elif call.data == "pay_paysafe":
        text_de = (
            "💳 PaySafe Code – Ganz unkompliziert:\n\n"
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


@bot.callback_query_handler(func=lambda call: call.data == "back_to_pay_options")
def callback_back_to_options(call):
    time_left = get_time_remaining()
    current_price = CURRENT_PRICE if time_left else OFFER_END_PRICE
    
    bot.answer_callback_query(call.id, "Zurück zu den Optionen... 🎀")

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"Schatz, wähle einfach, wie du mir den permanenten Zugang für {current_price} sichern möchtest! 🎀",
        reply_markup=generate_pay_options_markup()
    )


@bot.callback_query_handler(func=lambda call: call.data == "show_pay_options")
def callback_show_pay_options(call):
    time_left = get_time_remaining()
    current_price = CURRENT_PRICE if time_left else OFFER_END_PRICE

    bot.answer_callback_query(call.id, "Wunderbar, hier sind die Zahlungen! 💸")

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"Schatz, wähle einfach, wie du mir den permanenten Zugang für {current_price} sichern möchtest! 🎀",
        reply_markup=generate_pay_options_markup()
    )

@bot.callback_query_handler(func=lambda call: call.data == "show_info")
def callback_show_info(call):
    bot.answer_callback_query(call.id, "Zurück zur Übersicht! 🎀")

    time_left = get_time_remaining()
    
    if time_left:
        price_text = (
            f"🎉 Du hast Glück! Der permanente Zugang kostet aktuell nur {CURRENT_PRICE}.\n"
            f"Der Preis steigt in Kürze auf {OFFER_END_PRICE}!\n"
            f"⏰ BEEIL DICH! Du hast nur noch {time_left} Zeit! JETZT SICHERN! 💖\n\n"
        )
    else:
        price_text = (
            f"⚠️ Das zeitlich begrenzte Angebot ist leider abgelaufen. Der permanente Zugang kostet jetzt {OFFER_END_PRICE}.\n\n"
        )

    info_text_de = (
        "Hallo mein Schatz! Herzlich willkommen in meiner süßen Welt! 🥰\n\n"
        "Ich bin Emily, 19 Jahre alt, und ich stecke all meine Leidenschaft in heiße 18+ Videos! "
        "In meiner exklusiven VIP-Gruppe warten momentan ÜBER 70 SÜNDHAFT HEISSE VIDEOS auf dich! 🔥\n\n"
        "Außerdem findest du dort meine allerheißesten Inhalte und ich telefoniere auch ab und zu mit meinen treuesten Kunden, um eine ganz persönliche Verbindung aufzubauen! 📞💖\n\n"
        f"{price_text}"
        "Du kannst jetzt Zugang zu dieser tollen Community kaufen! "
        "Lass uns Spaß haben! ✨"
    )
    
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=info_text_de,
        reply_markup=generate_info_markup(),
        parse_mode="Markdown"
    )

# ----------------------------------------------------
# ZAHLUNGSNACHWEIS HANDLING
# ----------------------------------------------------

@bot.message_handler(content_types=["photo", "document"])
def handle_proof(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    
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
    
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="Vielen Dank für deine Bestätigung! Der Nachweis wird nun geprüft. ✅",
    )
    
    bot.forward_message(ADMIN_ID, proof_chat_id, proof_message_id)

    confirmation_text = (
        "Juhu! Danke dir, mein Schatz! 🌸🥰\n"
        "Ich habe deinen Zahlungsnachweis bekommen und sofort ganz schnell an meinen Admin weitergeleitet.\n"
        "Er prüft das jetzt ganz in Ruhe und meldet sich innerhalb der nächsten 5 MINUTEN persönlich bei dir! Freu dich! 💗\n\n"
        "Hier ist schon mal dein kleines, heißes Begrüßungsvideo 🎀✨"
    )
    bot.send_message(call.message.chat.id, confirmation_text)

    try:
        with open(WELCOME_VIDEO_PATH, "rb") as video:
            bot.send_video(call.message.chat.id, video)
    except FileNotFoundError:
        bot.send_message(call.message.chat.id, "Entschuldigung, das Begrüßungsvideo konnte nicht gefunden werden.")
    except Exception as e:
        bot.send_message(call.message.chat.id, f"Fehler beim Senden des Videos: {e}")

@bot.callback_query_handler(func=lambda call: call.data == "cancel_proof")
def cancel_proof_callback(call):
    bot.answer_callback_query(call.id, "Abgebrochen.")
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="Alles klar, Schatz. Wenn du den Nachweis später schicken möchtest, sende mir einfach das Bild oder Dokument! 💖",
    )
    
# Bot ignoriert normale Textnachrichten, die keine Befehle sind
@bot.message_handler(content_types=["text"])
def ignore_text(message):
    pass


# ----------------------------------------------------
# FLASK WEBHOOK HANDLER
# ----------------------------------------------------

# Flask-Route, die auf den Telegram-Webhook-Pfad reagiert
@app.route(WEBHOOK_URL_PATH, methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return '!', 200
    else:
        # Sollte nicht passieren, aber sichert ab.
        return 'Invalid request', 403


# Flask-Route für UptimeRobot/Render Health Check
@app.route('/')
def index():
    # Einfache Antwort für den Health Check
    return 'Bot Webhook Server is healthy', 200


# Startfunktion des Bots: Setzt den Webhook und startet Flask
def start_webhook():
    # Webhook setzen
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)
    
    print(f"Webhook gesetzt auf: {WEBHOOK_URL}")
    print(f"Flask Server startet auf Port {WEBHOOK_PORT}")
    
    # Starte den Flask-Server auf 0.0.0.0, damit Render ihn findet
    app.run(host='0.0.0.0', port=WEBHOOK_PORT)

# ----------------------------------------------------
# START BOT
# ----------------------------------------------------
if __name__ == '__main__':
    # Ausführung der Webhook-Startlogik
    start_webhook()
