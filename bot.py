import os
import telebot
from dotenv import load_dotenv
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta, timezone
from flask import Flask, request
import random 

# ----------------------------------------------------
# ZEIT-KONFIGURATION & TIMER-FUNKTION
# ----------------------------------------------------

# Die Zeitzone muss festgelegt werden (UTC, da Render-Server UTC nutzen)
TIMEZONE = timezone.utc 

# STARTDATUM DES ANGEBOTS (11.12.2025, 00:00:00 UTC)
# HINWEIS: Da jetzt 12:34 Uhr CET am 11.12.2025 ist, läuft das Angebot seit 11:34 Stunden.
OFFER_START_DATETIME = datetime(2025, 12, 11, 0, 0, 0).replace(tzinfo=TIMEZONE)

# Dauer des Angebots (9 Tage, 11 Stunden, 19 Minuten)
OFFER_DURATION = timedelta(days=9, hours=11, minutes=19)

def get_time_remaining():
    end_date = OFFER_START_DATETIME + OFFER_DURATION
    now = datetime.now(TIMEZONE)
    remaining = end_date - now
    
    if remaining.total_seconds() <= 0:
        return None 

    days = remaining.days
    seconds = int(remaining.total_seconds())
    
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    
    return f"{days} Tage, {hours % 24} Stunden und {minutes % 60} Minuten"
    

# ----------------------------------------------------
# DYNAMISCHE MITGLIEDER-SIMULATION
# ----------------------------------------------------

# Basis: Mindestanzahl an aktiven Mitgliedern
BASE_MEMBER_COUNT = 82 

# Simuliert die Fluktuation über 24 Stunden (Index = Stunde in UTC)
HOURLY_MEMBER_FLOW = [
    -2, -3, -3, -1, 0, 2, 3, 5, 8, 10, 12, 15, 14, 10, 8, 7, 9, 11, 13, 10, 7, 4, 2, 0 
]

def get_simulated_member_count():
    current_hour_utc = datetime.now(TIMEZONE).hour
    fluctuation = HOURLY_MEMBER_FLOW[current_hour_utc]
    
    # Zufälliger Offset für mehr Realismus ("mal kommt einer, mal geht einer")
    random_offset = random.randint(-1, 2)

    simulated_count = BASE_MEMBER_COUNT + fluctuation + random_offset
    
    return max(simulated_count, BASE_MEMBER_COUNT) # Sicherstellen, dass die Zahl nicht unter die Basis fällt


# ----------------------------------------------------
# CONFIG (Aus .env geladen)
# ----------------------------------------------------
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
# HIER SIND DIE VARIABLEN SO BENANNT, WIE DU SIE MIR GESENDET HAST:
ADMIN_ID = int(os.getenv("ADMIN_CHAT_ID"))   
VIP_CHANNEL = int(os.getenv("CHANNEL_ID"))     
WELCOME_VIDEO_ID = os.getenv("WELCOME_VIDEO_ID") 
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST")
# PUBLIC_CHANNEL_ID MUSS in Render gesetzt werden
PUBLIC_CHANNEL = int(os.getenv("PUBLIC_CHANNEL_ID", "-1003451305369")) 

# Zusätzliche Info
CURRENT_PRICE = "50€" 
OFFER_END_PRICE = "85€" 
DISPLAY_CHANNEL_LINK = "t.me/+mKdvOy5tByA3NGRh" 

# ----------------------------------------------------
# WEBHOOK-KONFIGURATION FÜR RENDER
# ----------------------------------------------------
WEBHOOK_PORT = int(os.environ.get('PORT', 5000)) 
WEBHOOK_URL_PATH = f"/{BOT_TOKEN}"
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

# PRÜFT MITGLIEDSCHAFT IM ÖFFENTLICHEN KANAL
def is_member(user_id):
    try:
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
    # Button für /start und /info (führt zu den Zahlungsoptionen)
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(
        InlineKeyboardButton("💕 Lass uns loslegen!", callback_data="show_pay_options")
    )
    return markup

# NEU: Markup für den Pflichtkanal-Beitritt
def generate_channel_join_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    # URL wird aus DISPLAY_CHANNEL_LINK erstellt
    markup.add(
        InlineKeyboardButton("👉 Jetzt Kanal beitreten", url=f"https://{DISPLAY_CHANNEL_LINK}")
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
    
    pay_markup = generate_info_markup() 
    member_count = get_simulated_member_count() 

    # 1. Wenn der Benutzer NICHT Mitglied ist -> Zwang zum Kanalbeitritt
    if not is_member(user_id):
        
        time_left = get_time_remaining()

        if time_left:
            price_text = (
                f"🎉 Glückwunsch! Du hast das ANGEBOT erwischt!\n"
                f"Der permanente Zugang kostet aktuell nur **{CURRENT_PRICE}**. Danach sind es **{OFFER_END_PRICE}**!\n"
                f"⏰ BEEIL DICH! Du hast nur noch **{time_left}** Zeit! JETZT SICHERN! 💖\n\n"
            )
        else:
            price_text = (
                f"⚠️ Das Angebot ist leider abgelaufen. Der permanente Zugang kostet jetzt **{OFFER_END_PRICE}**.\n\n"
            )

        text_de = (
            f"Ach, du lieber **{name}**! Willkommen in meiner süßen Welt! 🌸💖\n\n"
            f"In meiner exklusiven VIP-Gruppe sind momentan **{member_count} Member ON**! 🔥\n\n"
            f"{price_text}"
            "Damit wir uns von Anfang an verbunden fühlen und du keine meiner süßen Updates verpasst, "
            "tritt bitte kurz meinem ÖFFENTLICHEN KANAL bei, um fortzufahren.\n\n"
            "Klick einfach auf den Button unten. Ich freu mich auf dich! ✨"
        )
        bot.send_message(message.chat.id, text_de, parse_mode="Markdown", reply_markup=generate_channel_join_markup()) 
        return

    # 2. Wenn der Benutzer Mitglied ist (Bereit zur Zahlung/Nachweis)
    time_left = get_time_remaining()
    current_price = CURRENT_PRICE if time_left else OFFER_END_PRICE

    start_text_de = (
        f"Hallo mein lieber **{name}** 💕\n"
        "Toll, dass du dabei bist! Deine **permanente** VIP-Mitgliedschaft ist nur einen kleinen Schritt entfernt! 🌷✨\n\n"
        f"In meiner exklusiven VIP-Gruppe sind momentan **{member_count} Member ON**! 🔥\n\n"
        f"In der Gruppe warten **über 70 sündhaft heiße Videos** auf dich! Lass uns keine Zeit verlieren! 🔥\n\n"
        f"Der Zugang kostet aktuell nur **{current_price}**.\n\n"
        "Wenn du bereits gezahlt hast, sende mir bitte nur deinen **ZAHLUNGSNACHWEIS** (als Screenshot oder Dokument) und ich kümmere mich sofort um alles Weitere.\n\n"
    )
    
    bot.send_message(
        message.chat.id, 
        start_text_de, 
        reply_markup=pay_markup, # Führt zur Zahlung
        parse_mode="Markdown"
    )


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
    member_count = get_simulated_member_count() 

    if time_left:
        price_text = (
            f"🎉 Du hast Glück! Der permanente Zugang kostet aktuell nur **{CURRENT_PRICE}**.\n"
            f"Der Preis steigt in Kürze auf **{OFFER_END_PRICE}**!\n"
            f"⏰ BEEIL DICH! Du hast nur noch **{time_left}** Zeit! JETZT SICHERN! 💖\n\n"
        )
    else:
        price_text = (
            f"⚠️ Das zeitlich begrenzte Angebot ist leider abgelaufen. Der permanente Zugang kostet jetzt **{OFFER_END_PRICE}**.\n\n"
        )

    info_text_de = (
        "Hallo mein Schatz! Herzlich willkommen in meiner süßen Welt! 🥰\n\n"
        f"In meiner exklusiven VIP-Gruppe sind momentan **{member_count} Member ON**! 🔥\n\n"
        "Ich bin Emily, 19 Jahre alt, und ich stecke all meine Leidenschaft in heiße 18+ Videos! "
        
        "* **🎀 DAS ERWARTET DICH IM VIP BEREICH 🎀**\n"
        "* **Content-Flatrate:** Über **70 SÜNDHAFT HEISSE VIDEOS** und täglich neue, exklusive Bilder, die du nirgendwo anders findest! 🔥\n"
        "* **VIP-Treffen & Drehs:** Einmal pro Woche schreibe ich **1-2 meiner aktivsten Mitglieder persönlich** an, um sie auf ein intimes Treffen einzuladen – und vielleicht drehen wir dabei sogar ein exklusives Video! Sei bereit! 😈📞\n"
        "* **Persönlicher Austausch:** Ich antworte regelmäßig auf eure Nachrichten und kümmere mich liebevoll um meine Community! ❤️\n\n"
        
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
        "   - Verfolgung: Jede unautorisierte Weitergabe wird lückenlos verfolgt und dokumentiert.\n"
        "   - Datenerfassung: Durch Dritte wird automatisiert deine TELEFONNUMMER erfasst, um deine Identität zweifelsfrei festzustellen.\n"
        "   - Rechtliche Konsequenzen: Es werden umgehend rechtliche Schritte eingeleitet. Dein Zugang wird sofort und permanent gesperrt.\n\n"
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
    
    current_price = get_current_price_text() # Preis abrufen

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("⬅️ Zurück zu den Optionen", callback_data="back_to_pay_options"))

    if call.data == "pay_bank":
        text_de = (
            f"💸 Bank Überweisung (Preis: {current_price}) – Für unsere diskrete Abwicklung:\n\n"
            f"IBAN: `{IBAN}`\n"
            f"Empfänger: `{EMPFAENGER}`\n"
            f"BIC: `{BIC}`\n\n"
            "Wichtig: Bitte gib bei der Banküberweisung als Verwendungszweck unbedingt deinen Telegram-Benutzernamen an, damit ich dich zuordnen kann! ❤️"
        )
    elif call.data == "pay_crypto":
        text_de = (
            f"🪙 Krypto-Liebe (Preis: {current_price}) – Schnell und anonym:\n\n"
            f"Bitcoin: `{BTC}`\n"
            f"USDC / ETH: `{USDC_ETH}`"
        )
    elif call.data == "pay_paysafe":
        text_de = (
            f"💳 PaySafe Code (Preis: {current_price}) – Ganz unkompliziert:\n\n"
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
    member_count = get_simulated_member_count() 

    if time_left:
        price_text = (
            f"🎉 Du hast Glück! Der permanente Zugang kostet aktuell nur **{CURRENT_PRICE}**.\n"
            f"Der Preis steigt in Kürze auf **{OFFER_END_PRICE}**!\n"
            f"⏰ BEEIL DICH! Du hast nur noch **{time_left}** Zeit! JETZT SICHERN! 💖\n\n"
        )
    else:
        price_text = (
            f"⚠️ Das zeitlich begrenzte Angebot ist leider abgelaufen. Der permanente Zugang kostet jetzt **{OFFER_END_PRICE}**.\n\n"
        )

    info_text_de = (
        "Hallo mein Schatz! Herzlich willkommen in meiner süßen Welt! 🥰\n\n"
        f"In meiner exklusiven VIP-Gruppe sind momentan **{member_count} Member ON**! 🔥\n\n"
        "Ich bin Emily, 19 Jahre alt, und ich stecke all meine Leidenschaft in heiße 18+ Videos! "
        
        "* **🎀 DAS ERWARTET DICH IM VIP BEREICH 🎀**\n"
        "* **Content-Flatrate:** Über **70 SÜNDHAFT HEISSE VIDEOS** und täglich neue, exklusive Bilder, die du nirgendwo anders findest! 🔥\n"
        "* **VIP-Treffen & Drehs:** Einmal pro Woche schreibe ich **1-2 meiner aktivsten Mitglieder persönlich** an, um sie auf ein intimes Treffen einzuladen – und vielleicht drehen wir dabei sogar ein exklusives Video! Sei bereit! 😈📞\n"
        "* **Persönlicher Austausch:** Ich antworte regelmäßig auf eure Nachrichten und kümmere mich liebevoll um meine Community! ❤️\n\n"
        
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
    
    # Prüfe, ob der Benutzer im öffentlichen Kanal ist
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
    
    # 1. User-Informationen abrufen
    user_data = bot.get_chat(proof_chat_id)
    
    if user_data.username:
        source_info = f"@{user_data.username}"
    else:
        # Fallback: Chat ID
        source_info = f"Chat ID: `{user_data.id}`"
        
    # 2. Caption/Unterschrift für den Admin erstellen
    admin_caption = f"🚨 Money Came 💸 | {source_info}"

    # 3. Bestätigung beim Benutzer senden
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="Vielen Dank für deine Bestätigung! Der Nachweis wird nun geprüft. ✅",
    )
    
    # 4. Nachweis an den Admin weiterleiten (mit neuem Text VOR dem Forward)
    bot.send_message(
        ADMIN_ID, 
        admin_caption, 
        parse_mode="Markdown"
    )
    bot.forward_message(ADMIN_ID, proof_chat_id, proof_message_id)

    # 5. Bestätigung und Video an den Benutzer senden
    confirmation_text = (
        "Juhu! Danke dir, mein Schatz! 🌸🥰\n"
        "Ich habe deinen Zahlungsnachweis bekommen und sofort ganz schnell an meinen Admin weitergeleitet.\n"
        "Er prüft das jetzt ganz in Ruhe und meldet sich innerhalb der nächsten 5 MINUTEN persönlich bei dir! Freu dich! 💗\n\n"
        "Hier ist schon mal dein kleines, heißes Begrüßungsvideo 🎀✨"
    )
    bot.send_message(call.message.chat.id, confirmation_text)

    # Senden per ID
    try:
        if WELCOME_VIDEO_ID:
            bot.send_video(call.message.chat.id, WELCOME_VIDEO_ID)
        else:
            bot.send_message(call.message.chat.id, "Ups! Das Begrüßungsvideo lädt gerade nicht. Keine Sorge, mein Admin schickt es dir gleich persönlich! 💖")
    except Exception as e:
        print(f"Fehler beim Senden des Videos (ID: {WELCOME_VIDEO_ID}): {e}")
        bot.send_message(call.message.chat.id, "Entschuldigung, beim Senden des Videos gab es ein Problem. Mein Admin kümmert sich sofort darum! 💖")


@bot.callback_query_handler(func=lambda call: call.data == "cancel_proof")
def cancel_proof_callback(call):
    bot.answer_callback_query(call.id, "Abgebrochen.")
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="Alles klar, Schatz. Wenn du den Nachweis später schicken möchtest, sende mir einfach das Bild oder Dokument! 💖",
    )
    
# Bot fängt normale Nachrichten ab und leitet freundlich weiter
@bot.message_handler(content_types=["text"])
def ignore_text(message):
    if not message.text.startswith('/'):
        bot.send_message(
            message.chat.id, 
            f"Hey **{get_user_name(message)}**! Ich bin ein Bot und verstehe nur Befehle oder deinen Zahlungsnachweis. 🙈\n\n"
            f"Tippe ** /start ** oder ** /info ** um fortzufahren! 💖",
            parse_mode="Markdown"
        )


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
        return 'Invalid request', 403


# Flask-Route für UptimeRobot/Render Health Check
@app.route('/')
def index():
    return 'Bot Webhook Server is healthy', 200


# Startfunktion des Bots: Setzt den Webhook und startet Flask
def start_webhook():
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)
    
    print(f"Webhook gesetzt auf: {WEBHOOK_URL}")
    print(f"Flask Server startet auf Port {WEBHOOK_PORT}")
    
    app.run(host='0.0.0.0', port=WEBHOOK_PORT)

# ----------------------------------------------------
# START BOT
# ----------------------------------------------------
if __name__ == '__main__':
    start_webhook()
