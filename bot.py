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
# Wichtig: VIP_CHANNEL muss die NUMERISCHE ID des privaten Kanals sein.
VIP_CHANNEL = int(os.getenv("VIP_CHANNEL", -1003451305369)) 
WELCOME_VIDEO_PATH = "welcome.mp4" # Stelle sicher, dass diese Datei im selben Verzeichnis liegt

# Zusätzliche Info
PRICE_INFO = "50€ für permanenten Zugriff"
# Der tatsächliche Einladungslink für die Anzeige an den Benutzer (Muss der Pflichtkanal sein)
DISPLAY_CHANNEL_LINK = "t.me/+mKdvOy5tByA3NGRh"

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
# HELPER-FUNKTIONEN
# ----------------------------------------------------

# Funktion zur sicheren Abfrage des Vornamens
def get_user_name(message):
    """Gibt den Vornamen des Benutzers zurück oder einen liebevollen Standardnamen."""
    name = message.from_user.first_name
    return name if name else "Schatz"

# Funktion zum Überprüfen, ob ein Benutzer Mitglied des VIP-Kanals ist
def is_member(user_id):
    try:
        member = bot.get_chat_member(VIP_CHANNEL, user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        print(f"Fehler beim Überprüfen der Kanalmitgliedschaft: {e}")
        return False


# ----------------------------------------------------
# MARKUP-GENERIERUNG
# ----------------------------------------------------

# Markup für die Haupt-Zahlungsoptionen (mit "Zurück zur Info"-Button)
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

# Markup für den /info Befehl (führt zu den Zahlungen)
def generate_info_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(
        InlineKeyboardButton("💕 Lass uns loslegen!", callback_data="show_pay_options")
    )
    return markup


# ----------------------------------------------------
# COMMAND HANDLER
# ----------------------------------------------------

@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id
    name = get_user_name(message) # Name abfragen

    # Wenn der Benutzer NICHT Mitglied ist -> Gekürzte Info + Kanalbeitritt als Zwang
    if not is_member(user_id):
        # NEUER, REALISTISCHER TEXT FÜR DEN KANALBEITRITT
        text_de = (
            f"Ach, du lieber {name}! Willkommen in meiner süßen Welt! 🌸💖\n\n"
            "In meiner exklusiven VIP-Gruppe warten **über 70 sündhaft heiße Videos** auf dich, "
            "und ich telefoniere auch ab und zu mit meinen treuesten Kunden! 🔥📞\n\n"
            "Damit wir uns von Anfang an verbunden fühlen und du keine meiner süßen Updates verpasst, "
            "**tritt bitte kurz** meinem **öffentlichen Kanal** bei:\n"
            f"👉 {DISPLAY_CHANNEL_LINK}\n\n"
            f"Der permanente Zugang kostet nur **{PRICE_INFO}**.\n"
            "Komm danach sofort zurück! Ich freu mich auf dich! ✨"
        )
        bot.send_message(message.chat.id, text_de)
        return

    # Wenn der Benutzer Mitglied ist (Bereit zur Zahlung)
    start_text_de = (
        f"Hallo mein lieber {name} 💕\n"
        "Toll, dass du dabei bist! Momentan warten über **70 Videos** in der VIP-Gruppe darauf, von dir entdeckt zu werden! 🌷✨\n\n"
        "Jetzt fehlt nur noch ein kleiner Schritt, damit ich dich in die VIP-Gruppe schicken kann! \n"
        "Sende mir jetzt bitte nur noch deinen **Zahlungsnachweis**\n"
        "(am besten als Screenshot oder Dokument).  \n"
        "Ich kümmere mich dann sofort und ganz liebevoll um alles Weitere 🤍\n\n"
        "Falls du noch zahlen möchtest, nutze /pay für alle Optionen."
    )
    bot.send_message(message.chat.id, start_text_de)


@bot.message_handler(commands=["pay"])
def pay_options(message):
    bot.send_message(
        message.chat.id,
        f"Schatz, wähle einfach, wie du mir den **permanenten Zugang für {PRICE_INFO}** sichern möchtest! 🎀",
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
    # DIESER TEXT BLEIBT LANG UND DETAILLIERT
    info_text_de = (
        "Hallo mein Schatz! Herzlich willkommen in meiner süßen Welt! 🥰\n\n"
        "Ich bin Emily, 19 Jahre alt, und ich stecke all meine Leidenschaft in heiße 18+ Videos! "
        "In meiner exklusiven VIP-Gruppe warten momentan **über 70 sündhaft heiße Videos** auf dich! 🔥\n\n"
        "Außerdem findest du dort meine allerheißesten Inhalte und ich telefoniere auch ab und zu mit meinen treuesten Kunden, um eine ganz persönliche Verbindung aufzubauen! 📞💖\n\n"
        "Du kannst jetzt Zugang zu dieser tollen Community kaufen! "
        f"Der permanente Zugang kostet nur {PRICE_INFO}. Lass uns Spaß haben! ✨"
    )
    bot.send_message(message.chat.id, info_text_de, reply_markup=generate_info_markup())


@bot.message_handler(commands=["regeln", "rules"])
def rules(message):
    rules_text_de = (
        "Liebe ist Ordnung! Damit wir alle eine wunderschöne Zeit in der VIP-Gruppe haben, beachte bitte diese **unumgänglichen Regeln** zur Absicherung unserer Inhalte: ✨\n\n"
        "**1. Vertraulichkeit & Rechtliche Schritte (SEHR WICHTIG):**\n"
        "Mit dem Kauf des VIP-Zugangs bist du damit einverstanden, dass im Falle einer illegalen Weitergabe meiner Videos folgende Schritte eingeleitet werden:\n"
        "   - **Verfolgung:** Jede unautorisierte Weitergabe wird lückenlos verfolgt und dokumentiert.\n"
        "   - **Datenerfassung:** Durch Dritte wird automatisiert deine **Telefonnummer** erfasst, um deine Identität zweifelsfrei festzustellen.\n"
        "   - **Rechtliche Konsequenzen:** Es werden umgehend rechtliche Schritte eingeleitet. Dein Zugang wird sofort und permanent gesperrt.\n\n"
        "**2. Persönlicher Zugang:** Dein VIP-Zugang ist streng persönlich. Teile den Link oder die Inhalte niemals. 🚫\n"
        "**3. Respekt:** Sei lieb und respektvoll zu mir und anderen Mitgliedern. ❤️\n\n"
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
    # ... (Krypto und PaySafe Code Texte bleiben gleich)
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
    bot.answer_callback_query(call.id, "Zurück zu den Optionen... 🎀")

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"Schatz, wähle einfach, wie du mir den **permanenten Zugang für {PRICE_INFO}** sichern möchtest! 🎀",
        reply_markup=generate_pay_options_markup()
    )


@bot.callback_query_handler(func=lambda call: call.data == "show_pay_options")
def callback_show_pay_options(call):
    bot.answer_callback_query(call.id, "Wunderbar, hier sind die Zahlungen! 💸")

    # Bearbeitet die Nachricht, um direkt die Zahlungsoptionen anzuzeigen
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"Schatz, wähle einfach, wie du mir den **permanenten Zugang für {PRICE_INFO}** sichern möchtest! 🎀",
        reply_markup=generate_pay_options_markup()
    )

# Führt von /pay zurück zur /info Ansicht
@bot.callback_query_handler(func=lambda call: call.data == "show_info")
def callback_show_info(call):
    bot.answer_callback_query(call.id, "Zurück zur Übersicht! 🎀")

    # DETAIL-TEXT aus /info wird hier verwendet
    info_text_de = (
        "Hallo mein Schatz! Herzlich willkommen in meiner süßen Welt! 🥰\n\n"
        "Ich bin Emily, 19 Jahre alt, und ich stecke all meine Leidenschaft in heiße 18+ Videos! "
        "In meiner exklusiven VIP-Gruppe warten momentan **über 70 sündhaft heiße Videos** auf dich! 🔥\n\n"
        "Außerdem findest du dort meine allerheißesten Inhalte und ich telefoniere auch ab und zu mit meinen treuesten Kunden, um eine ganz persönliche Verbindung aufzubauen! 📞💖\n\n"
        "Du kannst jetzt Zugang zu dieser tollen Community kaufen! "
        f"Der permanente Zugang kostet nur {PRICE_INFO}. Lass uns Spaß haben! ✨"
    )
    
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=info_text_de,
        reply_markup=generate_info_markup() 
    )

# ----------------------------------------------------
# ZAHLUNGSNACHWEIS HANDLING UND FALLBACK
# ----------------------------------------------------

@bot.message_handler(content_types=["photo", "document"])
def handle_proof(message):
    user_id = message.from_user.id

    if not is_member(user_id):
        # ANGEPASSTER TEXT für den Fall, dass der Pflichtkanal fehlt
        bot.send_message(
            message.chat.id,
            f"Halt, stopp! Bevor du den Nachweis sendest, tritt bitte zuerst meinem öffentlichen Kanal bei:\n👉 {DISPLAY_CHANNEL_LINK}" 
        )
        return

    bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)

    confirmation_text = (
        "Juhu! Danke dir, mein Schatz! 🌸🥰\n"
        "Ich habe deinen Zahlungsnachweis bekommen und sofort ganz schnell an meinen Admin weitergeleitet.\n"
        "Er prüft das jetzt ganz in Ruhe und meldet sich **innerhalb der nächsten 5 Minuten** persönlich bei dir! Freu dich! 💗\n\n"
        "Hier ist schon mal dein kleines, heißes Begrüßungsvideo 🎀✨"
    )
    bot.send_message(message.chat.id, confirmation_text)

    try:
        with open(WELCOME_VIDEO_PATH, "rb") as video:
            bot.send_video(message.chat.id, video)
    except FileNotFoundError:
        bot.send_message(message.chat.id, "Entschuldigung, das Begrüßungsvideo konnte nicht gefunden werden.")
    except Exception as e:
        bot.send_message(message.chat.id, f"Fehler beim Senden des Videos: {e}")


@bot.message_handler(func=lambda m: True)
def fallback(message):
    name = get_user_name(message)
    # Fallback mit persönlicher Anrede und Button zum Bezahlen
    fallback_text = (
        f"Oh, mein lieber {name} 🥺🌺\n"
        "Du hast mir Text geschickt! Ich bin eine KI und verstehe gerade nur Befehle oder einen Zahlungsnachweis. \n\n"
        "Wenn du schon bezahlt hast, schicke mir bitte ein **Foto oder Dokument** deines Nachweises, damit ich alles schnell für dich freischalten kann! Ich will dich doch nicht warten lassen! 💖✨"
    )

    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("💸 Zu den Zahlungsmöglichkeiten", callback_data="show_pay_options")
    )

    bot.send_message(
        message.chat.id,
        fallback_text,
        reply_markup=markup
    )


# ----------------------------------------------------
# START BOT
# ----------------------------------------------------
print("Bot startet...")
bot.polling(none_stop=True)
