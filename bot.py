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
# HELPER → KANALCHECK
# Funktion zum Überprüfen, ob ein Benutzer Mitglied des VIP-Kanals ist
# ----------------------------------------------------
def is_member(user_id):
    try:
        # Hier wird die numerische ID des Kanals verwendet
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
# MARKUP-GENERIERUNG (Für den /info Befehl)
# ----------------------------------------------------
def generate_info_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    # Leitet den Benutzer direkt zum Zahlungs-Menü weiter
    markup.add(
        InlineKeyboardButton("💕 Lass uns loslegen!", callback_data="show_pay_options")
    )
    return markup


# ----------------------------------------------------
# /start COMMAND
# Handler für den /start Befehl
# ----------------------------------------------------
@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id

    # Überprüfe, ob der Benutzer Mitglied des VIP-Kanals ist
    if not is_member(user_id):
        # Nachricht, wenn der Benutzer NICHT Mitglied ist (liebevoller)
        text_de = (
            "Ach, du Süßer! Willkommen in meiner Welt! 🌸💖\n"
            "Wusstest du schon? In meiner VIP-Gruppe warten momentan über **70 heiße Videos** auf dich! 🔥\n\n"
            "Als ersten kleinen Schritt, tritt bitte kurz meinem **öffentlichen Kanal** bei, damit wir verbunden sind:\n\n"
            f"👉 {DISPLAY_CHANNEL_LINK}\n\n"
            f"Der permanente VIP-Zugang kostet nur {PRICE_INFO}.\n"
            "Komm danach sofort zurück, Süße! Ich warte auf dich! ✨"
        )
        bot.send_message(message.chat.id, text_de)
        return

    # Wenn der Benutzer Mitglied ist, sende die Begrüßungsnachricht (liebevoller)
    start_text_de = (
        "Hallo mein Schatz 💕\n"
        "Toll, dass du dabei bist! Momentan warten über **70 Videos** in der VIP-Gruppe darauf, von dir entdeckt zu werden! 🌷✨\n\n"
        "Jetzt fehlt nur noch ein kleiner Schritt, damit ich dich in die VIP-Gruppe schicken kann! \n"
        "Sende mir jetzt bitte nur noch deinen **Zahlungsnachweis**\n"
        "(am besten als Screenshot oder Dokument).  \n"
        "Ich kümmere mich dann sofort und ganz liebevoll um alles Weitere 🤍\n\n"
        "Falls du noch nicht bezahlt hast: /pay zeigt dir alle Optionen."
    )
    bot.send_message(message.chat.id, start_text_de)


# ----------------------------------------------------
# /pay COMMAND (Hauptbefehl für Zahlungsoptionen)
# ----------------------------------------------------
@bot.message_handler(commands=["pay"])
def pay_options(message):
    # Text weniger direkt auf Geldforderung ausgerichtet
    bot.send_message(
        message.chat.id,
        f"Schatz, wähle einfach, wie du mir den **permanenten Zugang für {PRICE_INFO}** sichern möchtest! 🎀",
        reply_markup=generate_pay_options_markup()
    )


# ----------------------------------------------------
# /support COMMAND
# Handler für den /support Befehl
# ----------------------------------------------------
@bot.message_handler(commands=["support"])
def support(message):
    support_text_de = (
        "Wenn du eine Frage hast oder Hilfe brauchst, schreibe bitte eine kurze Nachricht an @ProHvnter mit deinem Anliegen.\n"
        "Er wird sich schnellstmöglich um dich kümmern, damit alles reibungslos läuft! 💗"
    )
    bot.send_message(message.chat.id, support_text_de)


# ----------------------------------------------------
# /info COMMAND
# Handler für den /info Befehl
# ----------------------------------------------------
@bot.message_handler(commands=["info"])
def info(message):
    # Text mit 70 Videos, mehr Liebe und Telefonat-Info
    info_text_de = (
        "Hallo mein Schatz! Herzlich willkommen in meiner süßen Welt! 🥰\n\n"
        "Ich bin Emily, 19 Jahre alt, und ich stecke all meine Leidenschaft in heiße 18+ Videos! "
        "In meiner exklusiven VIP-Gruppe warten momentan **über 70 sündhaft heiße Videos** auf dich! 🔥\n\n"
        "Außerdem findest du dort meine allerheißesten Inhalte und ich telefoniere auch ab und zu mit meinen treuesten Kunden, um eine ganz persönliche Verbindung aufzubauen! 📞💖\n\n"
        "Du kannst jetzt Zugang zu dieser tollen Community kaufen! "
        f"Der permanente Zugang kostet nur {PRICE_INFO}. Lass uns Spaß haben! ✨"
    )
    # Button hinzugefügt, der zu den Zahlungsoptionen führt
    bot.send_message(message.chat.id, info_text_de, reply_markup=generate_info_markup())


# ----------------------------------------------------
# CALLBACK QUERY HANDLER (Reagiert auf Button-Klicks für Zahlungsdetails)
# ----------------------------------------------------
@bot.callback_query_handler(func=lambda call: call.data.startswith('pay_'))
def callback_payment_options(call):
    # Eindeutige Status-Nachricht beim Klick
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
    bot.answer_callback_query(call.id, "Zurück zu den Optionen... 🎀") # Bestätigt den Button-Klick

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"Schatz, wähle einfach, wie du mir den **permanenten Zugang für {PRICE_INFO}** sichern möchtest! 🎀",
        reply_markup=generate_pay_options_markup()
    )


# ----------------------------------------------------
# CALLBACK QUERY HANDLER (Reagiert auf Button bei /info)
# ----------------------------------------------------
@bot.callback_query_handler(func=lambda call: call.data == "show_pay_options")
def callback_show_pay_options(call):
    bot.answer_callback_query(call.id, "Wunderbar, hier sind die Zahlungen! 💸") # Bestätigt den Button-Klick

    # Bearbeitet die Nachricht, um direkt die Zahlungsoptionen anzuzeigen
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"Schatz, wähle einfach, wie du mir den **permanenten Zugang für {PRICE_INFO}** sichern möchtest! 🎀",
        reply_markup=generate_pay_options_markup()
    )


# ----------------------------------------------------
# ZAHLUNGSNACHWEIS HANDLING
# Handler für Fotos und Dokumente (Zahlungsnachweise)
# ----------------------------------------------------
@bot.message_handler(content_types=["photo", "document"])
def handle_proof(message):
    user_id = message.from_user.id

    # Überprüfe erneut die Kanalmitgliedschaft, bevor der Nachweis bearbeitet wird
    if not is_member(user_id):
        # Nachricht für den Fall, dass der Pflichtkanal fehlt
        bot.send_message(
            message.chat.id,
            f"Halt, stopp! Bevor du den Nachweis sendest, tritt bitte zuerst meinem öffentlichen Kanal bei:\n👉 {DISPLAY_CHANNEL_LINK}" 
        )
        return

    # Leite den Zahlungsnachweis an den Admin weiter
    bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)

    # Konsolidierte Bestätigungs- und Abschlussnachricht an den Benutzer (mit mehr Liebe)
    confirmation_text = (
        "Juhu! Danke dir, mein Schatz! 🌸🥰\n"
        "Ich habe deinen Zahlungsnachweis bekommen und sofort ganz schnell an meinen Admin weitergeleitet.\n"
        "Er prüft das jetzt ganz in Ruhe und meldet sich **innerhalb der nächsten 5 Minuten** persönlich bei dir! Freu dich! 💗\n\n"
        "Hier ist schon mal dein kleines, heißes Begrüßungsvideo 🎀✨"
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
    # Fallback mit mehr Liebe
    bot.send_message(
        message.chat.id,
        "Oh, mein Lieber 🥺🌺\n"
        "Du musst mir ein **Foto oder Dokument** deines Zahlungsnachweises schicken,\n"
        "damit ich alles schnell für dich freischalten kann! Ich will dich doch nicht warten lassen! 💖✨\n\n"
        "Wenn du noch bezahlen musst: /pay zeigt dir alle Möglichkeiten, wie wir das machen können!"
    )


# ----------------------------------------------------
# START BOT
# Starte den Bot und lasse ihn auf Nachrichten pollen
# ----------------------------------------------------
print("Bot startet...")
bot.polling(none_stop=True)
