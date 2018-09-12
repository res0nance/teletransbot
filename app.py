import telepot
import pprint
import telepot.loop
import telepot.namedtuple
import time
from datetime import datetime, timedelta
from googletrans import Translator
import os
import pycountry
import unicodedata
import wikipedia
import asyncio
import lyricwikia
import darklyrics


target_language = 'en'
isascii = lambda s: len(s) == len(s.encode())
allowed_languages = ['zh', 'ja', 'ms', 'id', 'tl']


bot        = None
translator = None

def init():
    global bot, translator
    translator = Translator()
    bot        = telepot.Bot(os.environ['telegram_apikey'])

def test_mode():
    global bot
    bot = None

def send_message(id, msg, **kwargs):
    if bot:
        bot.sendMessage(id,msg, **kwargs)

def main():
    init()
    pprint.pprint(bot.getMe())

    loop = asyncio.get_event_loop()
    loop.create_task(telepot.loop.MessageLoop(bot, {'chat': handle,
                                   'callback_query': on_callback_query}).run_forever())

    loop.run_forever()

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
        transpro = translate_object.pronunciation
        pprint.pprint(transtext)
        if transtext.lower().strip() != data.lower().strip():
            conf_rating = str(round(r.confidence,2))
            trans_msg = transtext + ' (' + transpro + ' : ' + pycountry.languages.get(alpha_2 = r.lang[:2]).name + ' : ' + conf_rating + ')'
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
            send_message(id, summary_results.split('\n')[0])
        except wikipedia.exceptions.DisambiguationError:
            buttons = []
            results = wikipedia.search(search_param)
            for result in results[1:]:
                buttons.append([telepot.namedtuple.InlineKeyboardButton(text=result, callback_data=result)])
            send_message(id, "Results for "+ search_param, reply_markup=telepot.namedtuple.InlineKeyboardMarkup(inline_keyboard=buttons))
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
                send_message(id, lyrics)
            except darklyrics.LyricsNotFound:
                send_message(id, 'No Lyrics found')
            return True
        elif len(song_param) == 2:
            try:
                lyrics = lyricwikia.get_lyrics(song_param[1],song_param[0])
                send_message(id, lyrics)
            except lyricwikia.LyricsNotFound:
                try:
                    lyrics = darklyrics.get_lyrics(song_param[0])
                    send_message(id, lyrics)
                except darklyrics.LyricsNotFound:
                    send_message(id, "No lyrics found")
            return True
    return False


def on_callback_query(msg):
    query_id, from_id, data = telepot.glance(msg, flavor='callback_query')
    print('Callback query:', query_id, from_id, data)
    pprint.pprint(msg)
    msg_idf = telepot.message_identifier(msg['message'])
    bot.editMessageText(msg_idf, wikipedia.summary(data))

def handle(msg):
    pprint.pprint(msg)

    if 'date' in msg:
        delta = datetime.utcnow() - datetime.utcfromtimestamp(msg['date'])
        if delta > timedelta(minutes = 1):
            return

    if 'text' in msg:
        message = msg['text']

        if handle_command(message, msg['chat']['id']):
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
            send_message(msg['chat']['id'], message, reply_to_message_id=msg['message_id'])


if __name__ == "__main__":
    main()
