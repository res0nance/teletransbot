import telepot
import pprint
import telepot.loop
import time
from googletrans import Translator
import os
import pycountry
import re


target_language = 'en'
isascii = lambda s: len(s) == len(s.encode())


bot = None
translator = None

def init():
    global bot, translator
    translator = Translator()
    bot = telepot.Bot(os.environ['telegram_apikey'])

def main():
    init()
    pprint.pprint(bot.getMe())
    telepot.loop.MessageLoop(bot,handle).run_as_thread()

    while 1:
        time.sleep(10)


def get_required_confidence(w):
    words = w.split()
    num_words = 0
    for word in words:
        stripped = word.strip()
        if stripped:
            num_words += 1
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
    r = translator.detect(text)
    conf = get_required_confidence(text)
    pprint.pprint(r.lang)
    pprint.pprint(r.confidence)
    pprint.pprint(conf)
    if r.lang != target_language and r.confidence >= conf:
        transtext = translator.translate(text,target_language).text
        if transtext.lower().strip() != text.lower().strip():
            return r.lang, transtext + ' (' + pycountry.languages.get(alpha_2 = r.lang[:2]).name
        + (' : .2f)' % r.confidence)
    return r.lang[:2], ""


def handle_command(text):
    commandtext = text.strip()
    commands = commandtext.split()

    if len(commands) == 2 and commands[0] == '/tlang' and len(commands[1]) == 2:
        try:
            lang_name = pycountry.languages.get(alpha_2 = commands[1])
            target_language = commands[1]
        except Exception e:
            pass
        return True
    return False



def handle(msg):
    pprint.pprint(msg)
    if 'text' in msg:
        message = msg['text']

        if msg['from']['username'] == os.environ['bot_admin'] and handle_command(message):
            return

        msglist   = split_words(message)
        translate = False
        translist = []
        moonrune  = False

        for w in msglist:
            lang, text = translate_text(w)
            if lang == 'zh' or lang == 'jp':
                moonrune = True
            if text:
                translist.append(text)
                translate = True
            else:
                translist.append(w)
        if not moonrune:
            lang, text = translate_text(message)
            if text:
                translate = True
                translist.clear()
                translist.append(text)
        if translate:
            message = ' '.join(translist)
            bot.sendMessage(msg['chat']['id'], message, reply_to_message_id=msg['message_id'])


if __name__ == "__main__":
    main()
