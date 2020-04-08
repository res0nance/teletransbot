import logging
import telegram
from telegram.error import NetworkError, Unauthorized
from time import sleep
import pprint
import time
from datetime import datetime, timedelta
from googletrans import Translator
import os
import pycountry
import unicodedata
import wikipedia
import lyricwikia
import darklyrics
import animelyrics

target_language = 'en'
isascii = lambda s: len(s) == len(s.encode())
allowed_languages = ['zh', 'ja', 'ms', 'id', 'tl', 'fr', 'ru']


bot        = None
translator = None
update_id  = None

def init():
    global bot, translator, update_id
    # bot        = telepot.Bot(os.environ['telegram_apikey'])
    translator = Translator()
    # Telegram Bot Authorization Token
    bot = telegram.Bot(os.environ['telegram_apikey'])

    # get the first pending update_id, this is so we can skip over it in case
    # we get an "Unauthorized" exception.
    try:
        update_id = bot.get_updates()[0].update_id
    except IndexError:
        update_id = None

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def test_mode():
    global bot
    bot = None

def send_message(id, msg, **kwargs):
    if bot:
        bot.send_message(id,msg, **kwargs)

def main():
    global update_id
    init()

    while True:
        try:
            # Request updates after the last update_id
            for update in bot.get_updates(offset=update_id, timeout=10):
                update_id = update.update_id + 1

                if update.callback_query:
                    on_callback_query(update.callback_query.id, update.callback_query.message.chat.id, update.callback_query.message.message_id, update.callback_query.data)
                elif update.message and update.message.text:  # your bot can receive updates without messages
                    # Reply to the message
                    handle(update.message.text, update.message.chat_id, update.message.message_id, update.message.date)
        except NetworkError:
            sleep(1)
        except Unauthorized:
            # The user has removed or blocked the bot.
            update_id += 1

def get_required_confidence(w):
    words     = w.split()
    num_words = 0

    for word in words:
        stripped        = word.strip()
        if stripped:
            num_words  += 1

    return max(0.575 - (num_words*0.05), 0.2)

def split_words(message):
    msglist = []
    currentWords = ""
    asciimode = True
    wordlist = message.split()
    for word in wordlist:
        swap = False
        for t in word:
            if not isascii(t) and asciimode:
                if currentWords:
                    msglist.append(currentWords)
                currentWords = word + ' '
                asciimode = not asciimode
                swap = True
                break
            elif isascii(t) and not asciimode:
                if currentWords:
                    msglist.append(currentWords)
                currentWords = word + ' '
                asciimode = not asciimode
                swap = True
                break
        if not swap:
            currentWords += word + ' '
    msglist.append(currentWords)
    return msglist

def translate_text(text):
    data = ''.join(c for c in unicodedata.normalize('NFC', text) if c <= '\uFFFF')
    r = translator.detect(data)
    conf = get_required_confidence(data)
    pprint.pprint(data)
    pprint.pprint(r.lang)
    pprint.pprint(r.confidence)
    pprint.pprint(conf)
    if r.lang != target_language and r.confidence >= conf and r.lang[:2] in allowed_languages:
        data = data.lower()
        translate_object = translator.translate(data,target_language)
        transtext = translate_object.text
        transpro = translate_object.pronunciation if translate_object.pronunciation else ''
        pprint.pprint(transtext)
        if transtext.lower().strip() != data.lower().strip():
            conf_rating = str(round(r.confidence,2))
            trans_msg = transtext + ' (' + pycountry.languages.get(alpha_2 = r.lang[:2]).name + ' : ' + conf_rating + ')'
            return r.lang[:2], trans_msg
    return "", ""


def handle_command(text,id):
    global target_language
    commandtext = text.strip()
    commands    = commandtext.split()
    print('Attempt to handle command')
    if len(commands) < 2:
        return False
    if commands[0] == '/wiki':
        print('Wiki Command')
        print(commands)
        search_param = ' '.join(commands[1:])
        try:
            summary_results = wikipedia.summary(search_param)
            send_message(id, summary_results.split('\n')[0], quote=False)
        except wikipedia.exceptions.DisambiguationError:
            buttons = []
            results = wikipedia.search(search_param)
            for result in results[1:]:
                buttons.append([telegram.InlineKeyboardButton(text=result, callback_data=result)])
            send_message(id, "Results for "+ search_param, reply_markup=telegram.InlineKeyboardMarkup(inline_keyboard=buttons))
        except wikipedia.exceptions.PageError:
            send_message(id, "No results found for " + search_param)
        return True
    elif commands[0] == '/lyrics':
        print('Lyrics command')
        song_param = ' '.join(commands[1:])
        song_param = song_param.split('by')
        if len(song_param) == 1:
            try:
                lyrics = darklyrics.get_lyrics(song_param[0])
                send_message(id, lyrics, quote=False)
            except darklyrics.LyricsNotFound:
                send_message(id, 'No Lyrics found', quote=False)
            return True
        elif len(song_param) == 2:
            try:
                lyrics = lyricwikia.get_lyrics(song_param[1],song_param[0])
                send_message(id, lyrics, quote=False)
            except lyricwikia.LyricsNotFound:
                try:
                    lyrics = darklyrics.get_lyrics(song_param[0])
                    send_message(id, lyrics, quote=False)
                except darklyrics.LyricsNotFound:
                    send_message(id, "No lyrics found", quote=False)
            return True
    elif commands[0] == '/animelyrics':
        print('Anime lyrics command')
        query = ' '.join(commands[1:])
        try:
            lyrics = animelyrics.search_lyrics(query)
            send_message(id, lyrics, quote=False)
        except animelyrics.NoLyricsFound:
            send_message(id, "No lyrics found", quote=False)
        return True
    return False


def on_callback_query(query_id, chat_id, msg_idf, data):
    bot.editMessageText(wikipedia.summary(data), chat_id=chat_id, message_id=msg_idf)

def handle(message, id, msg_id, date=None):

    if date != None:
        delta = datetime.utcnow() - date
        if delta > timedelta(minutes = 1):
            return

    if handle_command(message, id):
        return

    msglist   = split_words(message)
    pprint.pprint(msglist)
    translate = False
    translist = []

    if len(msglist) > 1:
        for w in msglist:
            lang, text = translate_text(w)
            if text:
                translist.append(text)
                translate = True
            else:
                translist.append(w)
    else:
        lang, text = translate_text(message)
        if text:
            translate = True
            translist.append(text)
    if translate:
        message = ' '.join(translist)
        send_message(id, message, quote=True, reply_to_message_id=msg_id)

if __name__ == "__main__":
    main()
