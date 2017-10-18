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
    words = w.split(' ')
    num_words = 0
    for word in words:
        stripped = word.strip()
        if stripped:
            num_words += 1
    return max(0.575 - (num_words*0.075), 0.1)

def split_words(message):
    msglist = []
    currentWords = ""
    asciimode = True
    wordlist = message.split()
    pprint.pprint(wordlist)
    for word in wordlist:
        swap = False
        for t in word:
            if not isascii(t) and asciimode:
                pprint.pprint(currentWords)
                if currentWords:
                    msglist.append(currentWords)
                currentWords = word + ' '
                asciimode = not asciimode
                swap = True
                break
            elif isascii(t) and not asciimode:
                pprint.pprint(currentWords)
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

def handle(msg):
    pprint.pprint(msg)
    if 'text' in msg:
        message = msg['text']
        msglist = split_words(message)
        translate = False
        translist = []
        moonrune  = False
        for w in msglist:
            r = translator.detect(w)
            conf = get_required_confidence(w)
            pprint.pprint(r.lang)
            pprint.pprint(r.confidence)
            pprint.pprint(conf)
            if r.lang[:2] == 'zh' or r.lang[:2] == 'jp':
                moonrune = True
            if r.lang != target_language and r.confidence >= conf:
                transtext = translator.translate(w,target_language).text
                if (transtext.lower() + ' ') != w.lower():
                    translist.append(transtext + ' (' + pycountry.languages.get(alpha_2=r.lang[:2]).name + ') ')
                    translate = True
                else:
                    translist.append(w + ' ')
            else:
                translist.append(w + ' ')
        if not moonrune:
            r = translator.detect(message)
            pprint.pprint(r.lang)
            pprint.pprint(r.confidence)
            conf = get_required_confidence(w)
            pprint.pprint(conf)
            if r.lang != target_language and r.confidence >= conf:
                transtext = translator.translate(message,target_language).text
                if transtext.lower() != message.lower():
                    translate = True
                    translist.clear()
                    translist.append(transtext + ' (' + pycountry.languages.get(alpha_2=r.lang[:2]).name + ') ')
        if translate:
            message = ''.join(translist)
            bot.sendMessage(msg['chat']['id'], message, reply_to_message_id=msg['message_id'])


if __name__ == "__main__":
    main()
